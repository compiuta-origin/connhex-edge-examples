package main

import (
	"os"
	"strconv"
	"time"

	"github.com/nats-io/nats.go"
)

type Config struct {
	NatsURL           string
	ServiceName       string
	HeartbeatInterval time.Duration
	MessageInterval   time.Duration
}

func getEnv(key string, fallback string) string {
	value := os.Getenv(key)
	if len(value) == 0 {
		return fallback
	}
	return value
}

func LoadConfig() (*Config, error) {
	heartbeatInterval, err := strconv.Atoi(getEnv("HEARTBEAT_INTERVAL_S", "10"))
	if err != nil {
		return nil, err
	}

	messageInterval, err := strconv.Atoi(getEnv("MESSAGE_INTERVAL_S", "60"))
	if err != nil {
		return nil, err
	}

	return &Config{
		NatsURL:           getEnv("NATS_URL", nats.DefaultURL),
		ServiceName:       getEnv("SERVICE_NAME", "custom_service"),
		HeartbeatInterval: time.Duration(heartbeatInterval) * time.Second,
		MessageInterval:   time.Duration(messageInterval) * time.Second,
	}, nil
}
