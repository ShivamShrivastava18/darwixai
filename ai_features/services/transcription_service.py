import google.generativeai as genai
import os
import time
from typing import Dict, List, Any
from django.conf import settings # Assuming Django settings for API key

class AudioTranscriptionService:
    def __init__(self):
        # Configure the Gemini API client
        if hasattr(settings, 'GOOGLE_API_KEY') and settings.GOOGLE_API_KEY:
            try:
                genai.configure(api_key=settings.GOOGLE_API_KEY)
                print(" Gemini API configured successfully.")
                self.model = genai.GenerativeModel('gemini-1.5-pro')
                print(" Gemini 2.5 Pro model initialized.")
            except Exception as e:
                print(f" Failed to configure Gemini API or load model: {e}")
                self.model = None
        else:
            print(" GOOGLE_API_KEY not found in settings. Gemini API disabled.")
            self.model = None
        

    def transcribe_with_diarization(self, audio_file_path: str) -> Dict[str, Any]:
        """
        Transcribe audio file with speaker diarization using the Gemini API.
        This version uses the Files API for better handling of larger audio.
        """
        if not self.model:
            return {
                "success": False,
                "error": "Gemini API model not available. Check GOOGLE_API_KEY.",
                "full_text": "",
                "segments": [],
                "speakers_count": 0,
                "duration": 0
            }

        # Ensure the input file exists
        if not os.path.exists(audio_file_path):
            return {
                "success": False,
                "error": f"Audio file not found: {audio_file_path}",
                "full_text": "",
                "segments": [],
                "speakers_count": 0,
                "duration": 0
            }

        file_upload_handle = None
        try:
            print(f" Uploading audio file to Gemini Files API: {audio_file_path}")
            
            # Step 1: Upload audio file to Gemini Files API
            # This creates a File object that can be referenced in generateContent requests
            file = genai.upload_file(path=audio_file_path)
            file_upload_handle = file # Keep track for deletion
            print(f" File uploaded to Gemini: {file.uri}")

            # Wait for file to become available for processing
            print(" Waiting for file processing...")
            while file.state.name == 'PROCESSING':
                print('.', end='', flush=True)
                time.sleep(10)
                file = genai.get_file(file.name)
            print(f"\n File state: {file.state.name}")

            if file.state.name != 'ACTIVE':
                return {
                    "success": False,
                    "error": f"File failed to process in Gemini Files API. State: {file.state.name}",
                    "full_text": "",
                    "segments": [],
                    "speakers_count": 0,
                    "duration": 0
                }
            
            # Step 2: Create the prompt for transcription and diarization
            prompt_parts = [
                "Transcribe the following audio, including speaker diarization. ",
                "Output should be structured with timestamps and speaker labels for each segment. ",
                "Please list all identified speakers at the end of the transcription, e.g., 'Speakers: SPEAKER_00, SPEAKER_01'.",
                file # Pass the File object directly
            ]

            print(" Sending transcription request to Gemini...")
            response = self.model.generate_content(prompt_parts)
            print(" Transcription response received.")

            # Step 3: Parse the response
            full_text = ""
            segments = []
            speakers_count = 0
            
            # Access the text from the response
            if response.text:
                full_text = response.text
            

                speaker_labels = set()
                
                # Split by lines and process segments
                for line in full_text.split('\n'):
                    line = line.strip()
                    if line.startswith('[') and ']' in line and ':' in line:
                        try:
                            # Extract time and speaker
                            time_speaker_part, text_part = line.split(':', 1)
                            
                            # Extract times
                            time_range_str = time_speaker_part[1:time_speaker_part.find(']')]
                            start_str, end_str = time_range_str.split(' - ')
                            
                            # Convert MM:SS to seconds (or HH:MM:SS)
                            start_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(start_str.split(':'))))
                            end_time = sum(float(x) * 60 ** i for i, x in enumerate(reversed(end_str.split(':'))))
                            
                            # Extract speaker
                            speaker = time_speaker_part[time_speaker_part.find(']') + 2:].strip()
                            
                            segments.append({
                                "start": start_time,
                                "end": end_time,
                                "text": text_part.strip(),
                                "speaker": speaker,
                                "confidence": 1.0 # Gemini doesn't expose confidence per segment directly like Whisper
                            })
                            speaker_labels.add(speaker)
                        except Exception as e:
                            print(f"Warning: Could not parse line '{line}'. Error: {e}")
                            # If parsing fails, just add as a simple text segment
                            segments.append({
                                "start": 0, # Placeholder
                                "end": 0,   # Placeholder
                                "text": line,
                                "speaker": "UNKNOWN",
                                "confidence": 0.0
                            })
            
                speakers_count = len(speaker_labels)
            
            # The duration is not directly returned by the transcription, but is from the input file
            # You might need to retrieve this if not already known, e.g., using a library like soundfile or librosa
            # For now, we'll assume the input audio's duration can be calculated.
            import soundfile as sf
            audio_info = sf.info(audio_file_path)
            duration = audio_info.duration


            return {
                "success": True,
                "language": "auto-detected", # Gemini handles this automatically
                "full_text": full_text,
                "segments": segments,
                "speakers_count": speakers_count,
                "duration": duration
            }

        except genai.APIError as e:
            print(f"Gemini API error: {e.args[0]}")
            return {
                "success": False,
                "error": f"Gemini API error: {e.args[0]}",
                "full_text": "",
                "segments": [],
                "speakers_count": 0,
                "duration": 0
            }
        except Exception as e:
            print(f"Transcription failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "full_text": "",
                "segments": [],
                "speakers_count": 0,
                "duration": 0
            }
        finally:
            # Clean up the uploaded file from Gemini's Files API
            if file_upload_handle:
                try:
                    print(f" Deleting uploaded file from Gemini: {file_upload_handle.name}")
                    genai.delete_file(file_upload_handle.name)
                    print("File deleted.")
                except Exception as e:
                    print(f"Warning: Failed to delete file from Gemini: {e}")
