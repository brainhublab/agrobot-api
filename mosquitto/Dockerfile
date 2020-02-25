FROM eclipse-mosquitto:1.5.6

COPY docker-entrypoint.sh /

COPY config/mosquitto.conf /
COPY config/access_control_list.acl /

ENTRYPOINT ["sh", "./docker-entrypoint.sh"]

CMD ["/usr/sbin/mosquitto", "-c", "/mosquitto.conf"]
