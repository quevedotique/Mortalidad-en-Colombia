import os
import tempfile


def azure_voice_available() -> bool:
    return bool(os.getenv("AZURE_SPEECH_KEY") and os.getenv("AZURE_SPEECH_REGION"))


def sintetizar_texto_azure(texto: str, voice_name: str = "es-MX-DaliaNeural") -> bytes | None:
    key = os.getenv("AZURE_SPEECH_KEY", "")
    region = os.getenv("AZURE_SPEECH_REGION", "")
    if not key or not region:
        return None

    import importlib
    try:
        speechsdk = importlib.import_module("azure.cognitiveservices.speech")
    except ModuleNotFoundError:
        print("ERROR: azure-cognitiveservices-speech no instalado")
        return None

    speech_config = speechsdk.SpeechConfig(subscription=key, region=region)
    speech_config.speech_synthesis_voice_name = voice_name
    speech_config.speech_synthesis_output_format = speechsdk.SpeechSynthesisOutputFormat.Riff16Khz16BitMonoPcm

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_file:
        temp_filename = temp_file.name

    audio_config = speechsdk.audio.AudioOutputConfig(filename=temp_filename)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)
    result = synthesizer.speak_text_async(texto).get()

    if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
        cancellation = speechsdk.SpeechSynthesisCancellationDetails(result)
        print("ERROR AZURE reason:", result.reason)
        print("ERROR AZURE code:", cancellation.error_code)
        print("ERROR AZURE detalle:", cancellation.error_details)
        try:
            os.remove(temp_filename)
        except OSError:
            pass
        return None

    try:
        with open(temp_filename, "rb") as f:
            audio_bytes = f.read()
    finally:
        try:
            os.remove(temp_filename)
        except OSError:
            pass

    return audio_bytes