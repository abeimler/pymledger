# https://github.com/adept/hledger-docker
FROM haskell:9.2.5 as hledger

ENV RESOLVER lts-20.8
ENV LC_ALL=C.UTF-8

RUN stack setup --resolver=$RESOLVER 
RUN stack install --resolver=$RESOLVER brick-1.6 fsnotify-0.4.1.0 hledger-lib-1.29.2 hledger-1.29.2 hledger-ui-1.29.2 hledger-web-1.29.2
RUN stack install --resolver=$RESOLVER hledger-stockquotes-0.1.2.1
RUN stack install --resolver=$RESOLVER hledger-interest-1.6.5
RUN stack install --resolver=$RESOLVER brick-1.6 hledger-lib-1.29.2 hledger-iadd-1.3.18
# RUN apt-get update && apt-get install -y python3-pip && pip3 install --prefix=/install git+https://gitlab.com/nobodyinperson/hledger-utils git+https://github.com/edkedk99/hledger-lots && rm -rf /var/lib/apt/lists

FROM debian:stable-slim as base

#MAINTAINER Dmitry Astapov <dastapov@gmail.com>

RUN apt-get update && apt-get install -y libgmp10 libtinfo6 sudo && rm -rf /var/lib/apt/lists
RUN adduser --system --ingroup root hledger && usermod -aG sudo hledger && mkdir /.cache && chmod 0777 /.cache
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

COPY --from=hledger /root/.local/bin/hledger* /usr/bin/
# COPY --from=hledger /install /usr/

ENV HLEDGER_HOST "0.0.0.0"
ENV HLEDGER_PORT "5000"
ENV HLEDGER_BASE_URL "http://localhost:$HLEDGER_PORT"
ENV HLEDGER_FILE_URL ""
ENV HLEDGER_JOURNAL_FILE "/data/hledger.journal"
ENV HLEDGER_DEBUG 1
ENV HLEDGER_RULES_FILE "/data/hledger.rules"
ENV HLEDGER_CAPABILITIES "view"
ENV HLEDGER_ARGS ""

ARG lang="C.UTF-8"
ENV LANG $lang
ENV LC_ALL $lang
ENV LANGUAGE $lang
RUN apt-get update && apt-get install -y locales && locale-gen ${lang} && dpkg-reconfigure locales && rm -rf /var/lib/apt/lists
RUN echo "${lang} UTF-8" | tee -a /etc/locale.gen && locale-gen

FROM base as python

RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    rm -rf /var/lib/apt/lists


FROM python as builder

RUN apt-get update && apt-get install -y git curl && rm -rf /var/lib/apt/lists
ADD "https://taskfile.dev/install.sh" /taskfile_install.sh
RUN chmod +x /taskfile_install.sh && /taskfile_install.sh -d -b /usr/local/bin

COPY . /home/hledger
COPY ./input /home/hledger/input
WORKDIR /home/hledger
ENV PYMLEDGER "/home/hledger/scripts/pymledger/pymledger.py"
ENV PYMLEDGER_CONFIG "/home/hledger/config.yml"
RUN git config --global --add safe.directory /home/hledger && chown -R hledger:root /home/hledger
RUN pip install -r /home/hledger/scripts/pymledger/requirements.txt

ENV PROJECT_DIR "/home/hledger"
ENV HLEDGER "/usr/bin/hledger"
ENV HLEDGER_WEB "/usr/bin/hledger-web"
RUN task generate check

ENV HLEDGER_ARGS "--auto"
ENV HLEDGER_JOURNAL_FILE "/home/hledger/all.hledger"
ENV LEDGER_FILE "/home/hledger/all.hledger"
ENV HLEDGER_RULES_FILE ""



FROM base as hledger-web

#COPY --from=builder /home/hledger/past_years /home/hledger/past_years
#COPY --from=builder /home/hledger/journals /home/hledger/journals
#COPY --from=builder /home/hledger/all.hledger /home/hledger/.hledger.journal
#COPY --from=builder /home/hledger/all.rules /home/hledger/.hledger.rules
#COPY --from=builder /home/hledger/all.aliases /home/hledger/.hledger.aliases
COPY --from=builder /home/hledger/journals/all.journal /home/hledger/.hledger.journal
ENV HLEDGER_ARGS "--auto"
ENV HLEDGER_JOURNAL_FILE "/home/hledger/.hledger.journal"
ENV LEDGER_FILE "/home/hledger/.hledger.journal"
ENV HLEDGER_RULES_FILE ""

COPY ./docker/start.sh /start.sh

ENV HLEDGER_PORT 5000
EXPOSE 5000

USER hledger
WORKDIR /home/hledger
CMD ["/start.sh"]


FROM base as hledger-web-api

#COPY --from=builder /home/hledger/past_years /home/hledger/past_years
#COPY --from=builder /home/hledger/journals /home/hledger/journals
#COPY --from=builder /home/hledger/all.hledger /home/hledger/.hledger.journal
#COPY --from=builder /home/hledger/all.rules /home/hledger/.hledger.rules
#COPY --from=builder /home/hledger/all.aliases /home/hledger/.hledger.aliases
COPY --from=builder /home/hledger/journals/all.journal /home/hledger/.hledger.journal
ENV HLEDGER_JOURNAL_FILE "/home/hledger/.hledger.journal"
ENV LEDGER_FILE "/home/hledger/.hledger.journal"
ENV HLEDGER_RULES_FILE ""

COPY ./docker/start-api.sh /start.sh

ENV HLEDGER_PORT 5001
EXPOSE 5001

USER hledger
WORKDIR /home/hledger
CMD ["/start.sh"]


FROM ubuntu:22.04 as ledger2beancount-setup

RUN apt-get update && apt-get install -y \
    git curl \
    build-essential \
    gcc-multilib \
    apt-utils \
    perl \
    expat \
    libexpat-dev \
    locales \
    cpanminus \
    && rm -rf /var/lib/apt/lists && rm -rf /tmp/* /var/tmp/*

FROM ledger2beancount-setup as ledger2beancount

RUN git clone https://github.com/beancount/ledger2beancount.git /usr/ledger2beancount
WORKDIR /usr/ledger2beancount
RUN cpanm --installdeps .

# Fix Perl warnings
ENV PATH="/usr/bin/perl:$PATH"
ARG lang="C.UTF-8"
ENV LANG "C.UTF-8"
ENV LC_ALL "C.UTF-8"
RUN apt-get update && apt-get install -y locales && locale-gen ${lang} && dpkg-reconfigure locales && rm -rf /var/lib/apt/lists
RUN echo "${lang} UTF-8" | tee -a /etc/locale.gen && locale-gen
# RUN locale-gen --purge "${lang}"
# RUN dpkg-reconfigure --frontend noninteractive locales

ENV LEDGER2BEANCOUNT "/usr/ledger2beancount/bin/ledger2beancount"
ENV PATH="/usr/ledger2beancount/bin/:$PATH"

ENTRYPOINT [ "/usr/ledger2beancount/bin/ledger2beancount" ]


FROM builder as ledger2beancount-builder

COPY --from=ledger2beancount /usr/ledger2beancount/bin/ledger2beancount /usr/ledger2beancount/bin/ledger2beancount
ENV LEDGER2BEANCOUNT "/usr/ledger2beancount/bin/ledger2beancount"

WORKDIR /home/hledger
ENV BEANCOUNT_FILE "/home/hledger/journals/all.beancount"
RUN $PYMLEDGER --hledger-path=$HLEDGER --ledger2beancount-path=$LEDGER2BEANCOUNT -c $PYMLEDGER_CONFIG beancount -f $HLEDGER_JOURNAL_FILE -o $BEANCOUNT_FILE


FROM yegle/fava as beancount
WORKDIR /bean
COPY --from=ledger2beancount-builder /home/hledger/journals/all.beancount /bean/all.bean
ENV BEANCOUNT_FILE "/bean/all.bean"
EXPOSE 5000