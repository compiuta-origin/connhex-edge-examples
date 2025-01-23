package main

import (
	"fmt"

	"github.com/nats-io/nats.go"
)

type Publisher interface {
	Publish(topic string, data []byte) error
	Drain() error
}

type StdoutPublisher struct {
}

func NewStdoutPublisher() *StdoutPublisher {
	return &StdoutPublisher{}
}

func (p *StdoutPublisher) Publish(topic string, data []byte) error {
	fmt.Printf("[%s] published: %s\n", topic, string(data))
	return nil
}

func (p *StdoutPublisher) Drain() error {
	return nil
}

type NatsPublisher struct {
	nc *nats.Conn
}

func NewNatsPublisher(nc *nats.Conn) *NatsPublisher {
	return &NatsPublisher{nc: nc}
}

func (p *NatsPublisher) Publish(topic string, data []byte) error {
	return p.nc.Publish(topic, data)
}

func (p *NatsPublisher) Drain() error {
	return p.nc.Drain()
}
