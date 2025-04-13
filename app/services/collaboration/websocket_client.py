import asyncio
import websockets
import json
import sys
import uuid

async def connect_websocket(user_id, session_id):
    uri = f"ws://localhost:8000/ws/{user_id}"
    async with websockets.connect(uri) as websocket:
        print(f"Connected as {user_id}")
        
        # Send join message
        join_message = {
            "type": "join_session",
            "session_id": session_id
        }
        await websocket.send(json.dumps(join_message))
        print(f"Sent join message for session {session_id}")
        
        # Create a task to handle user input
        async def handle_input():
            while True:
                try:
                    command = await asyncio.get_event_loop().run_in_executor(None, input, f"{user_id}> ")
                    if command.lower() == 'share':
                        # First create the document
                        document_id = str(uuid.uuid4())
                        create_message = {
                            "type": "share_document",
                            "session_id": session_id,
                            "document_id": document_id,
                            "document_content": "Hello, this is a test document!"
                        }
                        await websocket.send(json.dumps(create_message))
                        print(f"Created document with ID: {document_id}")
                        
                        # Lock the document before editing
                        lock_message = {
                            "type": "lock_document",
                            "session_id": session_id,
                            "document_id": document_id
                        }
                        await websocket.send(json.dumps(lock_message))
                        print(f"Locked document with ID: {document_id}")
                        
                        # Then edit it
                        edit_message = {
                            "type": "edit_document",
                            "session_id": session_id,
                            "document_id": document_id,
                            "content": "Hello, this is a test document!"
                        }
                        await websocket.send(json.dumps(edit_message))
                        print(f"Edited document with ID: {document_id}")
                        
                        # Unlock the document after editing
                        unlock_message = {
                            "type": "unlock_document",
                            "session_id": session_id,
                            "document_id": document_id
                        }
                        await websocket.send(json.dumps(unlock_message))
                        print(f"Unlocked document with ID: {document_id}")
                    elif command.lower() == 'quit':
                        # Send leave message before quitting
                        leave_message = {
                            "type": "leave_session",
                            "session_id": session_id
                        }
                        await websocket.send(json.dumps(leave_message))
                        break
                    else:
                        print("Available commands: 'share' to share a document, 'quit' to exit")
                except Exception as e:
                    print(f"Error handling input: {e}")
                    break

        # Create tasks for receiving messages and handling input
        receive_task = asyncio.create_task(handle_messages(websocket))
        input_task = asyncio.create_task(handle_input())

        try:
            # Wait for either task to complete
            done, pending = await asyncio.wait(
                [receive_task, input_task],
                return_when=asyncio.FIRST_COMPLETED
            )
        except asyncio.CancelledError:
            # Handle cancellation gracefully
            receive_task.cancel()
            input_task.cancel()
            try:
                await asyncio.gather(receive_task, input_task, return_exceptions=True)
            except Exception:
                pass
        finally:
            # Cancel any pending tasks
            for task in [receive_task, input_task]:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass

async def handle_messages(websocket):
    try:
        while True:
            message = await websocket.recv()
            try:
                # Try to parse and pretty print JSON messages
                data = json.loads(message)
                print(f"Received: {json.dumps(data, indent=2)}")
            except json.JSONDecodeError:
                # If not JSON, print as is
                print(f"Received: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Connection closed")
    except Exception as e:
        print(f"Error receiving message: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python websocket_client.py <user_id> <session_id>")
        sys.exit(1)
    
    user_id = sys.argv[1]
    session_id = sys.argv[2]
    
    try:
        asyncio.run(connect_websocket(user_id, session_id))
    except KeyboardInterrupt:
        print("\nDisconnected from server") 