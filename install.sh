#!/bin/bash


usage() {
    echo 'Usage: ./install.sh [-h | --help] --bot_token $BOT_TOKEN --chat_id $CHAT_ID --memo_api $MEMO_API'
    exit
}

SHORT=h,
LONG=help,bot_token:,chat_id:,memo_api:
OPTS=$(getopt -a -n build --options $SHORT --longoptions $LONG -- "$@")
if [ $? -ne 0 ]; then
    exit 1
fi


SERVICE=memosbot.service
BOT_TOKEN=
CHAT_ID=
MEMO_API=

eval set -- "$OPTS"
while true; do
    case "$1" in
        --bot_token )
            shift
            BOT_TOKEN=$1
            ;;
        --chat_id )
            shift
            CHAT_ID=$1
            ;;
        --memo_api )
            shift
            MEMO_API=$1
            ;;
        -h | --help)
            usage
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Unexpected option: $1"
            exit 2
            ;;
    esac
    shift
done

echo "BOT_TOKEN: $BOT_TOKEN"
echo "CHAT_ID: $CHAT_ID"
echo "MEMO_API: $MEMO_API"

if [ "$BOT_TOKEN" == "" ] || [ "$CHAT_ID" == "" ] || [ "$MEMO_API" == "" ]; then
    usage
fi

cat << EOF > /lib/systemd/system/$SERVICE
[Unit]
Description=Memos bot service
After=network.target

[Service]
Type=simple
Environment=BOT_TOKEN=$BOT_TOKEN
Environment=CHAT_ID=$CHAT_ID
Environment=MEMO_API=$MEMO_API
WorkingDirectory=/opt/usememos/MemosBot/
ExecStart=/usr/bin/python3 -u main.py run
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable --now $SERVICE
systemctl restart $SERVICE


