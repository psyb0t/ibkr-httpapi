# ibkr-httpapi — Go client

Typed Go client generated from `api/v1.yaml` via `oapi-codegen`.

## Install

```bash
go get github.com/psyb0t/ibkr-httpapi/pkg/clients/go@latest
```

## Use

```go
package main

import (
	"context"
	"fmt"
	"log"

	ibkr "github.com/psyb0t/ibkr-httpapi/pkg/clients/go"
)

func main() {
	c, err := ibkr.NewClientWithResponses("http://localhost:8889/v1",
		ibkr.WithRequestEditorFn(func(_ context.Context, req *http.Request) error {
			req.Header.Set("Authorization", "Bearer "+os.Getenv("IBKR_API_TOKEN"))
			return nil
		}),
	)
	if err != nil {
		log.Fatal(err)
	}

	resp, err := c.GetStockTickWithResponse(context.Background(), "AAPL", nil)
	if err != nil {
		log.Fatal(err)
	}
	fmt.Printf("AAPL last=%v\n", *resp.JSON200.Last)
}
```

## Regenerate

In the project root (where `api/v1.yaml` lives):

```bash
make generate-client-go
```

`client.gen.go` is a generated artifact — never hand-edit. Edit the spec and rerun the make target.
