package main

import (
	"fmt"
	"time"
)

type HeartbeatService struct {
	serviceName string
	p           Publisher
	ticker      *time.Ticker
	done        chan bool
}

func NewHeartbeatService(serviceName string, interval time.Duration, p Publisher) *HeartbeatService {
	h := &HeartbeatService{
		serviceName: serviceName,
		p:           p,
		ticker:      time.NewTicker(interval),
		done:        make(chan bool),
	}
	return h
}

func (h *HeartbeatService) Start() error {
	go func() {
		for {
			select {
			case <-h.done:
				return
			case <-h.ticker.C:
				fmt.Println("Sending heartbeat...")
				topic := fmt.Sprintf("heartbeat.%s.service", h.serviceName)
				h.p.Publish(topic, nil)
			}
		}
	}()

	return nil
}

func (h *HeartbeatService) Stop() error {
	fmt.Println("Stopping heartbeat...")

	if h.ticker != nil {
		h.ticker.Stop()
		h.done <- true
	}

	return nil
}
