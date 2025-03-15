import socket
import webbrowser
import time

def test_socket():
    # Create a socket server
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Try to bind to localhost
        server.bind(('127.0.0.1', 9999))
        print("Successfully bound to port 9999")
        
        # Listen for connections
        server.listen(1)
        print("\nSocket test server running!")
        print("Testing connection...")
        
        # Try to connect to ourselves
        time.sleep(1)  # Wait a bit
        try:
            test = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test.connect(('127.0.0.1', 9999))
            print("✅ Successfully connected to test socket!")
            test.close()
        except Exception as e:
            print("❌ Could not connect to test socket!")
            print(f"Error: {e}")
        
    except Exception as e:
        print(f"❌ Could not bind to port: {e}")
    finally:
        server.close()

if __name__ == "__main__":
    print("Starting basic network test...")
    print("This will test if your computer can make local connections.")
    test_socket() 