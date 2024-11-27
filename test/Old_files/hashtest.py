import base64

# Generate the processed key in Python
raw_key = "vl1m0RWFHItTWukMFNhggHgKZzYWa48xRBp/9oeZPCE=".encode('utf-8')[:16]
processed_key = base64.b64encode(raw_key).decode('utf-8')
print("Processed Key for Client:", processed_key)
