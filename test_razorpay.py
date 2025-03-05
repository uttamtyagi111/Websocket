import razorpay

client = razorpay.Client(auth=("rzp_test_YT2tRKBD7APCuv", "rQPrQ37umepgFmaXSLlduHe0"))

try:
    # Replace this with a harmless request or any test API call
    client.utility.create_order("test", "test", "test")
    print("Connection and authentication successful.")
except Exception as e:
    print(f"Error: {e}")
