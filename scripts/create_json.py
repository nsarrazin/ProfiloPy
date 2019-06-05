from profilopy.tools.jsonify import file_to_json, downsampler_mean, downsampler_random, downsampler_select

print("Afternoon file")
file_to_json("data/Wheel8 Aternoon.txt", -3619682275.496, file_out="afternoon.json")
print("Morning file")
file_to_json("data/Wheel8 Morning.txt", -3619671997.651, file_out="morning.json")

print("Generate downsampled files")
downsampler_random("data/afternoon.json", n=500)
downsampler_mean("data/afternoon.json", n=50)
downsampler_select("data/morning.json", [0])