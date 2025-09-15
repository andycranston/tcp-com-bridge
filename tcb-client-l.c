static char *version = "@(!--#) @(#) tcb-client-l.c, sversion 0.1.0, fversion 005, 14-september-2025";

/*
 *  tcb-client-l.c
 *
 *  TCP COM port bridge - client side
 *
 */

/**********************************************************************/

/*
 *  Links:
 *     https://www.geeksforgeeks.org/c/socket-programming-cc/
 *
 *  Notes:
 *
 */

/**********************************************************************/

/*
 *  includes
 */

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <string.h>
#include <ctype.h>
#include <fcntl.h>
#include <termios.h>
#include <poll.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <arpa/inet.h>

/**********************************************************************/

/*
 *  defines
 */

#ifndef TRUE
#define TRUE 1
#endif

#ifndef FALSE
#define FALSE 0
#endif

#define DEFAULT_POLL_TIMEOUT 10

#define DEFAULT_TCP_PORT 8089

#define DEVTTY "/dev/tty"

#define BUFFER_SIZE 8192

/**********************************************************************/

/*
 *  global variables
 */

char			*progname;

struct termios		originaltermoptions;
struct termios		termoptions;

/**********************************************************************/

void usage()
{
	fprintf(stderr, "%s: usage %s IPv4 address [ port ]\n", progname, progname);

	exit(2);
}

/**********************************************************************/

char *basename(s)
	char    *s;
{
	char    *bn;

	bn = s;

	while (*s != '\0') {
		if (*s == '/') {
			if (*(s+1) != '\0') {
				bn = s+1;
			}
		}

		s++;
	}

	return bn;
}

/**********************************************************************/

void writedev(devfd, s)
	int	devfd;
	char	*s;
{
	char	buf[BUFFER_SIZE];
	int	lens;
	int	i;

	lens = strlen(s);

	if (lens > 0) {
		for (i = 0; i < lens; i++) {
			buf[i] = s[i];
		}

		
		write(devfd, buf, lens);
	}

	return;
}

/**********************************************************************/

/*
 *  Main
 */

/* function */
int main(argc, argv)
	int     argc;
	char    *argv[];
{
	char			*ipv4;
	int			port;
	int			devtty;
	unsigned char		buf[8192];
	int			n;
	int			i;
	unsigned char		c;
	int			exitflag;
	struct pollfd		ttyfd[1];
	struct pollfd		sockfd[1];
	int			pollretcode;
	int			clientsocket;
	struct sockaddr_in	serv_addr;

	progname = basename(argv[0]);

	if ((argc < 2) || (argc > 3)) {
		usage();
	}

	ipv4 = argv[1];

	if (argc == 3) {
		port = atoi(argv[2]);
	} else {
		port = DEFAULT_TCP_PORT;
	}

	if ((devtty = open(DEVTTY, O_RDWR)) == -1) {
		fprintf(stderr, "%s: unable to open %s\n", progname, DEVTTY);
	}

	tcgetattr(devtty, &originaltermoptions);

	tcgetattr(devtty, &termoptions);

	cfmakeraw(&termoptions);

	tcsetattr(devtty, TCSANOW, &termoptions);

	if ((clientsocket = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
		fprintf(stderr, "%s: unable to create a TCP (stream) based socket\n", progname);
		exit(2);
	}

	serv_addr.sin_family = AF_INET;
	serv_addr.sin_port   = htons(port);

	if (inet_pton(AF_INET, ipv4, &serv_addr.sin_addr) <= 0) {
		fprintf(stderr, "%s: invalid IP address \"%s\"\n", progname, ipv4);
		exit(2);
	}

	if (connect(clientsocket, (struct sockaddr*)&serv_addr, sizeof(serv_addr)) < 0) {
		fprintf(stderr, "%s: connection to %s:%d failed\n", progname, ipv4, port);
		exit(2);
	}


	writedev(devtty, "<<Connected>>\r\n");

	exitflag = FALSE;

	while (! exitflag) {
		ttyfd[0].fd      = devtty;
		ttyfd[0].events  = POLLIN;

		/*
		printf("----------------\n");
		*/

		pollretcode = poll(ttyfd, (nfds_t)1, DEFAULT_POLL_TIMEOUT);

		if (pollretcode < 0) {
			fprintf(stderr, "%s: call to tty poll gave a negative return code of %d\n", progname, pollretcode);
			exit(2);
		}

		if (pollretcode > 0) {
			n = read(devtty, buf, 8192);

			if (n < 0) {
				fprintf(stderr, "%s: tty poll said there was data but error when trying to read the data\n", progname);
				exit(2);
			}

			if (n == 0) {
				fprintf(stderr, "%s: tty poll said there was data but read returned no data\n", progname);
				exit(2);
			}

			for (i = 0; i < n; i++) {
				/*
				printf("%d\t%c\n", i, buf[i]);
				*/

				if (buf[i] == '^') {
					exitflag = TRUE;
					break;
				}
			}

			/* if exit time break out now */
			if (exitflag) {
				break;
			}

			/* send the data */
			send(clientsocket, buf, n, 0);
		}

		sockfd[0].fd      = clientsocket;
		sockfd[0].events  = POLLIN;

		pollretcode = poll(sockfd, (nfds_t)1, DEFAULT_POLL_TIMEOUT);

		if (pollretcode < 0) {
			fprintf(stderr, "%s: call to socket poll gave a negative return code of %d\n", progname, pollretcode);
			exit(2);
		}

		if (pollretcode > 0) {
			n = read(clientsocket, buf, 8192);

			if (n < 0) {
				fprintf(stderr, "%s: socket poll said there was data but error when trying to read the data\n", progname);
				exit(2);
			}

			if (n == 0) {
				fprintf(stderr, "%s: socket poll said there was data but read returned no data\n", progname);
				exit(2);
			}

			for (i = 0; i < n; i++) {
				if ((buf[i] >= 32) && (buf[i] <=126) || (buf[i] == 8) || (buf[i] == 10) || (buf[i] == 13)) {
					write(devtty, buf+i, 1);
				}
			}
		}
	}

	writedev(devtty, "\r\n<<Exiting>>\r\n");

	/*
	buf[0] = '\n';
        buf[1] = '\r';
	write(devtty, buf, 2);
	*/

	tcsetattr(devtty, TCSANOW, &originaltermoptions);

	close(devtty);

	return 0;
}

/**********************************************************************/

/* end of file: tcb-client-l.c */
