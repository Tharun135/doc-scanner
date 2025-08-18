from transformers import pipeline
generator = pipeline("text-generation", model="gpt2")
print(generator("Hello, world!", max_length=20))