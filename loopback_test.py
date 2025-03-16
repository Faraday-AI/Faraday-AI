import socket

def test_loopback():
    print("Testing ONLY loopback interface (should work regardless of network)...")
    
    # Create server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    
    try:
        # Bind explicitly to loopback
        server.bind(('localhost', 12345))
        print("✅ Successfully bound to localhost:12345")
        server.listen(1)
        print("Listening for test connection...")
        
        # Try to connect to ourselves
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect(('localhost', 12345))
        print("✅ Successfully connected to test socket!")
        print("\nThis means your local networking is working!")
        print("If web browsers still can't connect, it might be a browser security setting.")
        client.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nThis indicates a fundamental networking issue on your machine.")
    finally:
        server.close()

if __name__ == "__main__":
    test_loopback() 