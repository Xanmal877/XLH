

print("Loading model...")
config = XttsConfig()
config.load_json("Noelle\config.json")
model = Xtts.init_from_config(config)
model.load_checkpoint(config, checkpoint_dir="Noelle", use_deepspeed=False)
model.cuda()

print("Computing speaker latents...")
gpt_cond_latent, speaker_embedding = model.get_conditioning_latents(audio_path=["NoelleVocals.wav"])

print("Inference...")
out = model.inference(
    "Merry Christmas to my wonderful Family!",
    "en",
    gpt_cond_latent,
    speaker_embedding,
    temperature=0.7, # Add custom parameters here
)
torchaudio.save("xtts.wav", torch.tensor(out["wav"]).unsqueeze(0), 24000)