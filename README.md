[![Deploy](https://github.com/coolworld2049/fastapi-ecommerce/actions/workflows/deploy.yml/badge.svg)](https://github.com/coolworld2049/fastapi-ecommerce/actions/workflows/deploy.yml)

<div>
<img src="assets/fastapi-logo.png" alt="fastapi-logo" height="60" /> 
<img src="assets/postgres.png" alt="postgres-logo" height="60" /> 
<img src="assets/mongodb-logo.png" alt="mongodb-logo" height="60" />
<img src="assets/prisma-logo.png" alt="prisma-logo" height="60" />
</div>

---

# [auth_service](auth_service)

![auth-service.png](assets%2Fauth-service.png)

![auth-service-user-table.png](assets%2Fauth-service-user-table.png)

# [store_service](store_service)

![store_service.png](assets%2Fstore_service.png)

```prisma
generator client {
  provider               = "prisma-client-py"
  partial_type_generator = "./prisma/partial_types.py"
  interface              = asyncio
  recursive_type_depth   = 8
}

datasource db {
  provider = "mongodb"
  url      = env("MONGODB_URL")
}

enum OrderStatus {
  pending
  awaiting_payment
  awaiting_fulfilment
  completed
  canceled
  declined
  refunded
  disputed
  partially_refunded
  deleted
}

model Category {
  id          String    @id @default(auto()) @map("_id") @db.ObjectId
  name        String    @unique
  description String?   
  created_at  DateTime? @default(now())
  updated_at  DateTime? @updatedAt
  products    Product[] 
}

model Product {
  id             String         @id @default(auto()) @map("_id") @db.ObjectId
  title          String         @unique
  stock          Int            
  price          Float          
  description    String?        
  created_at     DateTime?      @default(now())
  updated_at     DateTime?      @updatedAt
  category       Category       @relation(fields: [category_id], references: [id])
  category_id    String         @db.ObjectId
  order_products OrderProduct[] 
}

model Order {
  id             String         @id @default(auto()) @map("_id") @db.ObjectId
  status         OrderStatus    @default(pending)
  cost           Float?         
  created_at     DateTime?      @default(now())
  updated_at     DateTime?      @updatedAt
  user_id        String         
  order_products OrderProduct[] 
}

model OrderProduct {
  id         String   @id @default(auto()) @map("_id") @db.ObjectId
  order      Order    @relation(fields: [order_id], references: [id])
  order_id   String   @db.ObjectId
  product    Product? @relation(fields: [product_id], references: [id])
  product_id String?  @db.ObjectId
}
```

![prisma-studio.png](assets%2Fprisma-studio.png)

## dev mode
.env
```text
STAGE=dev
```
add the following lines to /etc/hosts
```text
127.0.0.1 auth-service.fastapi-ecommerce.com
127.0.0.1 store-service.fastapi-ecommerce.com
```
