package main

import (
	"fmt"
)

type Service struct {
	hs *HeartbeatService
	ms *MessageService
}

func NewService(hb *HeartbeatService, ms *MessageService) *Service {
	s := &Service{hs: hb, ms: ms}
	return s
}

func (s *Service) Start() error {
	fmt.Println("Starting service...")

	if err := s.hs.Start(); err != nil {
		return err
	}

	if err := s.ms.Start(); err != nil {
		return err
	}

	return nil
}

func (s *Service) Stop() error {
	fmt.Println("Stopping service...")

	if err := s.hs.Stop(); err != nil {
		return err
	}

	if err := s.ms.Stop(); err != nil {
		return err
	}

	return nil
}
