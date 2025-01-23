package main

import (
	"fmt"
	"os"
	"os/signal"
	"syscall"

	"github.com/nats-io/nats.go"
)

// TODO: add logger
func main() {
	config, err := LoadConfig()
	if err != nil {
		fmt.Println("Cannot load config")
		os.Exit(1)
	}
	fmt.Printf("Loaded config: %+v\n", *config)

	nc, err := nats.Connect(config.NatsURL)
	if err != nil {
		fmt.Println("Cannot connect to NATS")
		os.Exit(1)
	}
	p := NewNatsPublisher(nc)
	defer p.Drain()

	hb := NewHeartbeatService(config.ServiceName, config.HeartbeatInterval, p)
	ms := NewMessageService(config.MessageInterval, p)
	svc := NewService(hb, ms)
	if err := svc.Start(); err != nil {
		fmt.Println("Error starting service")
		os.Exit(1)
	}
	defer svc.Stop()

	c := make(chan os.Signal, 1)
	signal.Notify(c, syscall.SIGINT, syscall.SIGTERM)
	<-c
}
