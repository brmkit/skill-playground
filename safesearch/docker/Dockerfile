FROM alpine:3.19

RUN apk add --no-cache curl python3 lynx

COPY search.sh /usr/local/bin/search.sh
COPY parse_results.py /usr/local/bin/parse_results.py
COPY injection_patterns.py /usr/local/bin/injection_patterns.py
RUN chmod +x /usr/local/bin/search.sh

ENTRYPOINT ["/usr/local/bin/search.sh"]
