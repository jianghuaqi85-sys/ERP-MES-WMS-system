package config

import (
	"fmt"

	"github.com/spf13/viper"
)

// Config holds the application configuration.
type Config struct {
	Server ServerConfig `mapstructure:"server"`
	Logger LoggerConfig `mapstructure:"logger"`
}

type ServerConfig struct {
	Port int    `mapstructure:"port"`
	Mode string `mapstructure:"mode"`
}

type LoggerConfig struct {
	Level    string `mapstructure:"level"`
	Encoding string `mapstructure:"encoding"`
}

// LoadConfig reads the configuration from the specified path and unmarshals it into the Config struct.
func LoadConfig() (*Config, error) {
	v := viper.New()
	v.SetConfigFile("configs/config.yaml") // hardcoded for now, can be injected later
	v.SetConfigType("yaml")

	// Set defaults
	v.SetDefault("server.port", 8080)
	v.SetDefault("server.mode", "development")
	v.SetDefault("logger.level", "debug")
	v.SetDefault("logger.encoding", "console")

	if err := v.ReadInConfig(); err != nil {
		return nil, fmt.Errorf("failed to read config file: %w", err)
	}

	var cfg Config
	if err := v.Unmarshal(&cfg); err != nil {
		return nil, fmt.Errorf("failed to unmarshal config: %w", err)
	}

	return &cfg, nil
}
