package main

import (
	"encoding/json"
	"errors"
	"fmt"
	"math/rand"
	"time"
)

var ErrGenerateMessage = errors.New("Error generating message")

type MessageService struct {
	p      Publisher
	ticker *time.Ticker
	done   chan bool
}

type message struct {
	Name  string `json:"name"`
	Time  int64  `json:"time"`
	Value int    `json:"value"`
}

func NewMessageService(interval time.Duration, p Publisher) *MessageService {
	m := &MessageService{
		p:      p,
		ticker: time.NewTicker(interval),
		done:   make(chan bool),
	}
	return m
}

func (m *MessageService) Start() error {
	go func() {
		for {
			select {
			case <-m.done:
				return
			case <-m.ticker.C:
				msg, err := m.getMessage()
				if err != nil {
					fmt.Println("Error generating message")
				}
				fmt.Printf("Sending message: %s\n", msg)

				topic := "events.data"
				m.p.Publish(topic, msg)
			}
		}
	}()

	return nil
}

func (m *MessageService) Stop() error {
	fmt.Println("Stopping message service...")

	if m.ticker != nil {
		m.ticker.Stop()
		m.done <- true
	}

	return nil
}

func (m *MessageService) getMessage() ([]byte, error) {
	msg := message{
		Name:  "cpt:device:123:temperature",
		Time:  time.Now().Unix(),
		Value: rand.Intn(100),
	}

	res, err := json.Marshal(msg)
	if err != nil {
		return nil, fmt.Errorf("error marshalling message: %w", ErrGenerateMessage)
	}

	return []byte(res), nil
}
