# fastapi-mongo-ecommerce

---
## Features
  * product search, including category selection, keyword search and price filters and other features
  * adding items to the cart and calculating the total cost of the order

### RBAC
* admin
  * has full access to the database, including the ability to add, edit and delete products and users.
* manager 
  * has access to product management, but cannot manage users.
* customer
  * can only view products and place orders.
* guest
  * does not have access to the personal account and can only view products.

### Prisma ODM
- ### Many-to-many relation
  * schema.prisma
    ```prisma
      model Product {
        id          String    @id @default(auto()) @map("_id") @db.ObjectId
        carts       Cart[]    @relation(fields: [cart_ids], references: [id])
        cart_ids    String[]  @db.ObjectId
      }
    
      model Cart {
        id          String      @id @default(auto()) @map("_id") @db.ObjectId
        products    Product[]   @relation(fields: [product_ids], references: [id])
        product_ids String[]    @db.ObjectId
      } 
    ```
  * partial_types.py
      ```python
      Cart.create_partial("CartWithoutRelations", exclude_relational_fields=True)

      Cart.create_partial(
            "CartProductInput",
            exclude_relational_fields=True,
            exclude=["id", "expires_at", "status"],
      )
      ```
      - api endpoints
        * add_products_to_cart
          ```python
          @router.patch(
            "/{cart_id}/add_products",
            response_model=CartWithoutRelations,
            )
            async def add_products_to_cart(
                  cart_id: str,
                  product_ids: CartProductInput,
            ) -> Optional[Cart]:
                  data = {"products": {"set": [{"id": x} for x in product_ids.product_ids]}}
                  new_cart = await Cart.prisma().update(
                      data=data,
                      where={"id": cart_id},
                      include={"products": True}
                  )
                  return new_cart
          ```
          * test
            * request
              ``` python
              curl -X 'PATCH' \
                'http://localhost:8000/api/v1/carts/6402191237ac0a87071f095f/add_products' \
                -H 'accept: application/json' \
                -H 'Content-Type: application/json' \
                -d '{
                "product_ids": ["640210e1084f14833838f9c8"]
              }'
              ```
            * response
              ```python
              {
                "product_ids": [
                  "64020a7a2219272a89e26e9c"
                ]
              }
              ```
