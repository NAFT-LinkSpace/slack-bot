#!/bin/sh

set -eu

cd "$(dirname "$0")"

compose_profiles=""

case "${1:-}" in
	"")
		compose_profiles="--profile slack-bot --profile rocketchat"
		;;
	rocketchat)
		compose_profiles="--profile rocketchat"
		;;
	slack-bot)
		compose_profiles="--profile slack-bot"
		;;
	*)
		echo "Usage: $0 [rocketchat|slack-bot]" >&2
		exit 1
		;;
esac

exec docker compose ${compose_profiles} up -d
