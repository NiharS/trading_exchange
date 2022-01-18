## Trading Exchange

This project is a simple trading exchange platform replica allowing users to buy and sell stocks with cash. Cash is represented in cents throughout this project, to prevent floating point errors.

### Running

The project can be run using `docker-compose`:
```
docker-compose build
docker-compose up
```
These commands will spin up 4 containers:
- A Postgres DB
- A RabbitMQ queue
- An API server
- An order matcher

The first two are the standard services and just have their images pulled from dockerhub. The API server is a Flask server that handles CRUD operations on the resources in the DB, and the order matcher is a queue-consumer process that matches orders.

### Interacting with the service

The API server starts on port 5000 on the host (this can be modified in the `docker-compose.yml` file). There's a helper script (scripts/seed_exchange.py) that will create a few basic users with some initial assets of cash and stock.

The following APIs are currently supported:
- /api/v1/users
  - GET: gets all users in the exchange
  - POST: creates a user
- "/api/v1/users/<user_id>
  - GET: gets a single user
- /api/v1/users/<user_id>/orders
  - GET: get the user's orders. Add ?status=<completed/active> to filter
  - POST: create an order for the user
- /api/v1/orders
  - GET: gets all orders in the system. add ?status=<completed/active> to filter
- /api/v1/users/<user_id>/orders/<order_id>
  - DELETE: delete an order. If an order has been partially processed, don't process it any further

### Matching orders

Orders are matched based on buyers willing to pay more than a seller is willing to sell an asset.

When a sell order comes in, the matcher looks for existing buy orders for the asset with the same or higher price, and uses the buy order's price to make the trade. The matcher prioritizes the highest buy price, then takes the oldest order if the buy prices are equal. If either order isn't fully completed by the trade, the remaining amount is notated in the order so the rest can be completed later.

When a buy order comes in, the matcher checks for sellers