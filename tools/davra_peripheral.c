// Server code
#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#define PORT 12345

int main()
{
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[1024] = {0};

    // Creating socket
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0)
    {
        perror("socket failed");
        exit(EXIT_FAILURE);
    }

    // Set SO_REUSEADDR socket option
    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt)) < 0)
    {
        perror("setsockopt");
        exit(EXIT_FAILURE);
    }

    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    // Binding socket
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0)
    {
        perror("bind failed");
        exit(EXIT_FAILURE);
    }

    // Listening for connections
    if (listen(server_fd, 3) < 0)
    {
        perror("listen");
        exit(EXIT_FAILURE);
    }

    while (1)
    {
        // Accepting connection
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen)) < 0)
        {
            perror("accept");
            exit(EXIT_FAILURE);
        }

        // Receiving message
        ssize_t bytes_read;
        while ((bytes_read = read(new_socket, buffer, 1024)) > 0)
        {
            buffer[bytes_read] = '\0'; // Null-terminate the received string
            printf("Message received: %s\n", buffer);
            // Sending response
            const char *response = "Message received";
            ssize_t bytes_to_send = strlen(response);
            ssize_t bytes_sent = send(new_socket, response, bytes_to_send, 0);

            if (bytes_sent < 0)
            {
                perror("send failed");
            }
            else if (bytes_sent != bytes_to_send)
            {
                printf("Partial message sent. Bytes sent: %zd, expected: %zd\n", bytes_sent, bytes_to_send);
            }
            else
            {
                printf("Message sent successfully\n");
            }
        }
    }

    return 0;
}
