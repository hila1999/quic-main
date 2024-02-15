import asyncio
import socket
import time

async def handle_stream(stream_socket, port):
    print(f"Started handling stream {port}")
    total_bytes = 0  # Variable to keep track of total bytes received
    total_packets = 0  # Variable to keep track of total packets received
    start_time = time.time()  # Start time
    try:
        while True:
            data, _ = stream_socket.recvfrom(1024)
            message = data.decode()
            print(f"Received chunk from stream {port}: {message}")
            if message == "EXIT":
                print(f"Received exit signal from stream {port}. Stopping...")
                break
            total_bytes += len(data)  # Update total bytes received
            total_packets += 1  # Update total packets received
            await asyncio.sleep(0)  
    except Exception as e:
        print(f"Exception occurred in stream {port}: {e}")
    finally:
        end_time = time.time()  # End time
        time_elapsed = end_time - start_time  # Time elapsed
        if time_elapsed > 0:
            average_data_rate = total_bytes / time_elapsed  # Calculate average data rate
            average_packet_rate = total_packets / time_elapsed  # Calculate average packet rate
            print(f"Average data rate in stream {port}: {average_data_rate:.2f} bytes/second")
            print(f"Average packet rate in stream {port}: {average_packet_rate:.2f} packets/second")
        # print(f"Total bytes passed in stream {port}: {total_bytes}")  # Print total bytes passed
        # print(f"Total packets passed in stream {port}: {total_packets}")  # Print total packets passed
        stream_socket.close()
        return total_bytes, total_packets  # Return the total bytes and packets

async def receive_file():
    # Create a UDP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # Server address and port
    server_address = ('localhost', 12345)

    # Bind the socket to the server address
    server_socket.bind(server_address)
    num_streams = 0
    total_bytes_all_streams = 0  # Variable to keep track of total bytes received across all streams
    total_packets_all_streams = 0  # Variable to keep track of total packets received across all streams
    start_time_all_streams = time.time()  # Start time for all streams
    try:
        while True:
            # Receive number of streams
            data, _ = server_socket.recvfrom(1024)
            msg = data.decode()
            print(msg)
            if msg == "CLOSE":
                break
            num_streams = int(msg.split(':')[1])

            print(f"Received number of streams: {num_streams}")
            if num_streams > 20:
                break
            ports = []
            for i in range(num_streams):
                data, _ = server_socket.recvfrom(1024)
                print(data.decode())
                port_num = int(data.decode().split(':')[1])
                ports = ports + [port_num]

            # Start a coroutine for each stream
            tasks = []
            for i in range(num_streams):
                port = ports[i]  # Base port + stream index
                print(f"num streams is: {num_streams}")
                print(f"Creating task for stream {port}")
                stream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                stream_socket.bind(('localhost', port))
                print(f"Bound stream socket to port {port}")
                task = asyncio.create_task(handle_stream(stream_socket, port))
                tasks.append(task)

            # Wait for all tasks to complete
            for task in asyncio.as_completed(tasks):
                total_bytes, total_packets = await task
                total_bytes_all_streams += total_bytes
                total_packets_all_streams += total_packets

        end_time_all_streams = time.time()  # End time for all streams
        time_elapsed_all_streams = end_time_all_streams - start_time_all_streams  # Time elapsed for all streams
        if time_elapsed_all_streams > 0:
            total_data_rate = total_bytes_all_streams / time_elapsed_all_streams  # Calculate total data rate
            total_packet_rate = total_packets_all_streams / time_elapsed_all_streams  # Calculate total packet rate
            print(f"Total data rate across all streams: {total_data_rate:.2f} bytes/second")
            print(f"Total packet rate across all streams: {total_packet_rate:.2f} packets/second")

    finally:
        # Close socket
        server_socket.close()

if __name__ == "__main__":
    asyncio.run(receive_file())
