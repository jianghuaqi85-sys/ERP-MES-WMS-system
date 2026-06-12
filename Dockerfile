# ==============================================================================
# Stage 1: Build the Go binary
# ==============================================================================
FROM golang:1.21-alpine AS builder

# Set Go environment variables for faster and static build
ENV GOPROXY=https://goproxy.cn,direct \
    CGO_ENABLED=0 \
    GOOS=linux \
    GOARCH=amd64

WORKDIR /app

# Cache dependencies
COPY go.mod go.sum ./
RUN go mod download

# Copy the rest of the source code
COPY . .

# Build the application.
# -w disables DWARF debugging information
# -s disables symbol table
# These ldflags significantly reduce the binary size and prevent reverse engineering
RUN go build -ldflags="-w -s" -o main ./cmd/server/main.go

# ==============================================================================
# Stage 2: Create a minimal, secure production image
# ==============================================================================
# We can use scratch for the absolute smallest image, or alpine if we need basic shell tools.
# Alpine is chosen here for timezone and basic debugging capabilities if absolutely needed.
FROM alpine:latest

# Add timezone data and set timezone to Asia/Shanghai
RUN apk --no-cache add tzdata && \
    cp /usr/share/zoneinfo/Asia/Shanghai /etc/localtime && \
    echo "Asia/Shanghai" > /etc/timezone && \
    apk del tzdata

# Create a non-root user and group for security
RUN addgroup -S erpapp && adduser -S erpapp -G erpapp
USER erpapp

WORKDIR /app

# Copy the binary and config files from the builder stage
COPY --from=builder /app/main .
COPY --from=builder /app/configs/config.yaml ./configs/
COPY --from=builder /app/configs/rbac_model.conf ./configs/

# Expose the application port
EXPOSE 8080

# Run the binary
CMD ["./main"]
