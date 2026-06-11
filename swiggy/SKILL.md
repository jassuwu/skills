---
name: swiggy
description: Order food, groceries, and book restaurants via Swiggy MCP — covers Food, Instamart, and Dineout
triggers:
  - "order food"
  - "order groceries"
  - "swiggy"
  - "instamart"
  - "dineout"
  - "book restaurant"
  - "book table"
  - "grocery list"
  - "meal prep"
  - "order dinner"
  - "order lunch"
  - "order breakfast"
  - "weekly groceries"
  - "recipe ingredients"
  - "party supplies"
  - "reorder"
  - "track order"
  - "track delivery"
---

# Swiggy

Operates Swiggy end-to-end via MCP tools across three verticals:
**Food** (restaurant delivery), **Instamart** (groceries in minutes),
and **Dineout** (table reservations).

## MCP Tools Available

### Swiggy Food (`swiggy-food`)
| Tool | What it does |
|------|-------------|
| `get_addresses` | User's saved delivery addresses |
| `search_restaurants` | Find restaurants by dish, cuisine, or name |
| `search_menu` | Search items across restaurant menus |
| `get_restaurant_menu` | Full menu for a specific restaurant |
| `get_food_cart` | Current cart with bill breakdown |
| `update_food_cart` | Add/update/remove cart items |
| `flush_food_cart` | Clear the entire food cart |
| `place_food_order` | Place the order (**COD only**) |
| `fetch_food_coupons` | Available coupons and offers |
| `apply_food_coupon` | Apply a coupon to the order |
| `get_food_orders` | Past and current orders |
| `get_food_order_details` | Details of a specific order |
| `track_food_order` | Track active delivery |

### Swiggy Instamart (`swiggy-instamart`)
| Tool | What it does |
|------|-------------|
| `get_addresses` | User's saved delivery addresses |
| `search_products` | Find products by name, category, or brand |
| `get_cart` | Current grocery cart with cost breakdown |
| `update_cart` | Add/update/remove items |
| `clear_cart` | Clear entire grocery cart |
| `checkout` | Place the grocery order (**COD only**) |
| `get_orders` | Past and current Instamart orders |
| `track_order` | Track grocery delivery |

### Swiggy Dineout (`swiggy-dineout`)
| Tool | What it does |
|------|-------------|
| `get_saved_locations` | User's saved/preferred locations |
| `search_restaurants_dineout` | Find restaurants by location & preferences |
| `get_restaurant_details` | Menu, ratings, pricing, offers |
| `get_available_slots` | Booking time slots for a date |
| `book_table` | Reserve a table (**free bookings only**) |
| `create_cart` | Create a reservation cart |
| `get_booking_status` | Check booking status |

---

## Safety Rules

**Read these before every order. Non-negotiable.**

1. **NEVER place an order without explicit user confirmation.**
   Always show the complete cart (items, quantities, prices, total)
   and ask "Should I place this order?" before calling `place_food_order`,
   `checkout`, or `book_table`.

2. **All orders are Cash on Delivery (COD).** Remind the user of this
   before placing any order. No online payment is available via MCP.

3. **Orders cannot be cancelled** once placed through MCP.
   Make this clear before checkout. Double-check the cart.

4. **Keep the Swiggy app closed.** Using the Swiggy mobile app
   simultaneously causes session conflicts and order failures.
   Warn the user if they mention they have the app open.

5. **If a tool call fails**, retry once. If it fails again, tell the
   user and suggest they check if the Swiggy app is closed / try again
   in a minute. Do not retry silently in a loop.

---

## Workflows

### 1. Grocery Shopping (Instamart) — Primary Workflow

This is the most common use case. Follow this sequence.

#### 1a. Quick grocery order

1. `get_addresses` — confirm delivery address. Ask user to pick one
   if multiple are saved. Lock this in before searching.
2. Parse what the user needs into a shopping list.
3. For each item: `search_products` with specific terms.
   - Use brand name if the user specified one.
   - If multiple results, pick the best match by relevance and value.
   - If ambiguous (e.g., multiple pack sizes), ask the user.
4. `update_cart` — add each item with the correct quantity.
5. `get_cart` — show the full cart as a table:
   ```
   | # | Item                    | Qty | Price  |
   |---|-------------------------|-----|--------|
   | 1 | Amul Toned Milk 500ml   | 2   | ₹54    |
   | 2 | Aashirvaad Atta 5kg     | 1   | ₹299   |
   |   | **Total**               |     | **₹353** |
   ```
6. Ask: "Cart ready. Total is ₹{total} (COD). Should I place the order?"
7. Only on explicit "yes" / "place it" / "go ahead" → `checkout`.
8. Confirm: "Order placed! Track with 'track my order'."

#### 1b. Recipe-to-cart

1. User provides a recipe name or description.
2. Break it down into ingredients with approximate quantities for the
   stated serving size. Show the ingredient list to the user first.
3. `get_addresses` — confirm address.
4. For each ingredient: `search_products`.
   - Map recipe quantities to available pack sizes
     (e.g., "200g paneer" → search "paneer 200g", pick closest pack).
   - Skip items the user likely already has (salt, water, basic oil)
     unless they say "add everything."
5. Build cart, show summary, confirm, checkout per step 1a.

#### 1c. Weekly meal prep

1. Ask the user for:
   - Number of days (default 5)
   - Dietary preferences (veg/non-veg, keto, high-protein, etc.)
   - Budget (optional)
2. Generate a meal plan with breakfast/lunch/dinner.
3. Consolidate all ingredients into a single grocery list,
   combining duplicates (e.g., 3 recipes need onions → total quantity).
4. Proceed with 1b flow using the consolidated list.

#### 1d. Budget-constrained shopping

1. Ask for the budget upfront.
2. Track a running total as items are added.
3. After each `search_products`, pick the most cost-effective option
   (larger pack size per ₹, store brand over premium).
4. If approaching the limit (>85%), warn:
   "Running total: ₹{x} of ₹{budget}. {remaining} left."
5. If an item would exceed the budget, suggest a cheaper alternative
   or ask the user which item to drop.

#### 1e. Reorder previous groceries

1. `get_orders` — fetch recent Instamart orders.
2. Show the last 3-5 orders with date and item summary.
3. User picks one (or says "last order").
4. Rebuild the cart from that order's items.
5. Show cart, confirm, checkout.

#### 1f. Brand comparison

When the user asks to compare brands:
1. `search_products` for the product category.
2. Present a comparison table:
   ```
   | Brand       | Pack Size | Price | Per kg/L |
   |-------------|-----------|-------|----------|
   | Fortune     | 1L        | ₹175  | ₹175/L   |
   | Sundrop     | 1L        | ₹155  | ₹155/L   |
   | Saffola     | 1L        | ₹199  | ₹199/L   |
   ```
3. Let the user pick.

### 2. Food Ordering

#### 2a. Quick food order

1. `get_addresses` — confirm delivery address.
2. Understand the craving: cuisine, dish, dietary restriction, budget.
3. `search_restaurants` or `search_menu` based on specificity:
   - Vague ("hungry", "something good") → `search_restaurants` by cuisine
   - Specific ("butter chicken") → `search_menu` for the dish
4. Present top 3-5 options:
   ```
   | # | Restaurant        | Rating | Time  | Price Range |
   |---|-------------------|--------|-------|-------------|
   | 1 | Meghana Foods     | 4.3⭐  | 25min | ₹₹          |
   | 2 | Paradise Biryani  | 4.1⭐  | 35min | ₹₹          |
   ```
5. User picks a restaurant.
6. `get_restaurant_menu` — show relevant menu sections.
7. `update_food_cart` — add items as user chooses.
8. `fetch_food_coupons` — check for discounts. If any apply,
   `apply_food_coupon` with the best one.
9. `get_food_cart` — show final bill with discount applied.
10. Ask for confirmation → `place_food_order`.

#### 2b. Group / office order

1. Gather: headcount, budget per person, dietary mix (veg/non-veg ratio).
2. Find restaurants with variety (thalis, combos work well for groups).
3. Build a balanced order:
   - Calculate items needed based on headcount
   - Mix dishes to cover preferences
   - Stay within per-person budget
4. Show order with per-person breakdown.
5. Confirm → place.

#### 2c. Late night / fast delivery

1. `search_restaurants` — filter results by delivery time.
2. Prioritize restaurants showing <30min delivery.
3. If nothing is available, say so honestly.

### 3. Restaurant Booking (Dineout)

1. `get_saved_locations` — identify the user's area.
2. Ask for: cuisine, party size, date, preferred time, area (if not obvious).
3. `search_restaurants_dineout` — find matching restaurants.
4. Present options with ratings, offers, price range.
5. User picks one → `get_restaurant_details` for full info.
6. `get_available_slots` — show available time slots for the chosen date.
7. User picks a slot → `book_table`.
8. `get_booking_status` — confirm the reservation.

**Note:** Only free bookings are supported. If the restaurant requires a paid booking, inform the user and suggest they book via the app.

### 4. Order Tracking

When the user asks to track an order:

- Food: `track_food_order` — show delivery status, ETA, rider details.
- Instamart: `track_order` — show delivery status and ETA.
- Dineout: `get_booking_status` — show reservation confirmation.

If the user just says "track my order" without specifying which,
check both `track_food_order` and `track_order` and report whichever
has an active delivery.

### 5. Combined Workflows

#### Party planning

1. Ask: guest count, type (house party vs dining out), budget, date.
2. **If house party:**
   - Instamart: snacks, beverages, ice, cups/plates/napkins, decorations
   - Food: order catered dishes from a restaurant closer to party time
3. **If dining out:**
   - Dineout: find & book a restaurant that fits the group
   - Instamart: optional (flowers, gifts, pre-party supplies)

#### Date night

1. Dineout: book a romantic restaurant.
2. Instamart: order flowers/wine/candles for home delivery (before or after).

---

## Diet Shortcuts

When the user mentions a diet, translate to search terms:

| Diet | Search terms for Instamart |
|------|---------------------------|
| **Keto** | chicken, eggs, cheese, butter, nuts, coconut oil, avocado, paneer, cream, almond flour |
| **Vegan** | tofu, plant milk (oat/soy/almond), tempeh, nutritional yeast, fresh vegetables, legumes |
| **High-protein** | chicken breast, eggs, paneer, greek yogurt, whey protein, lentils, chickpeas, peanut butter |
| **Gluten-free** | rice, quinoa, millets (ragi, jowar, bajra), buckwheat, rice flour, oats (GF-labeled) |
| **Low-carb** | cauliflower, zucchini, mushrooms, eggs, fish, chicken, nuts, seeds, leafy greens |

For Food orders, include these terms in `search_menu` queries to find
diet-appropriate restaurant dishes.

---

## Presentation Rules

- Use tables for any list of 3+ items (cart, search results, comparisons).
- Always show prices with ₹ symbol.
- Show running totals when building carts.
- Keep item names concise — brand + product + size (e.g., "Amul Butter 500g").
- When presenting restaurants: name, rating, delivery time, price range.
- When presenting products: name, brand, pack size, price.
- Don't dump raw API responses. Curate and format.

---

## State

Store recurring preferences and lists in
`~/.openclaw/skills/swiggy/state.json`:

```json
{
  "preferredAddress": "Home",
  "weeklyStaples": [],
  "dietaryPreferences": [],
  "favoriteBrands": {},
  "lastGroceryOrder": null
}
```

- **preferredAddress**: auto-select this address instead of asking every time.
  Set when the user says "always deliver to home" or after 3 consecutive
  orders to the same address.
- **weeklyStaples**: items the user orders every week. Build this up over
  time from order history. Suggest "want to reorder your usual staples?"
- **dietaryPreferences**: persistent diet tags (e.g., ["vegetarian", "no-onion"]).
  Apply as filters in every search unless overridden.
- **favoriteBrands**: product → brand mapping (e.g., {"milk": "Amul", "atta": "Aashirvaad"}).
  Prefer these brands in search results.
- **lastGroceryOrder**: timestamp + order ID for quick reorder.

Update state after each completed order. Read state at the start of
every interaction to apply saved preferences.

---

## Cron: Weekly Grocery Reminder

If the user sets up a weekly grocery routine, configure a cron via OpenClaw:

- **When**: User says "remind me to order groceries every Sunday" or similar.
- **Action**: At the scheduled time, send a message:
  ```
  🛒 Weekly grocery time! Want me to reorder your usual staples?

  Last order (Mar 12): Milk, Bread, Eggs, Atta, Dal, Rice, Onions, Tomatoes
  Total was ₹847

  Say "reorder" to repeat, or tell me what's different this week.
  ```
- Pull the last grocery order from `state.json` or via `get_orders`.
- If the user says "reorder" → rebuild and confirm cart.
- If they modify → adjust accordingly.

---

## Error Recovery

| Problem | Action |
|---------|--------|
| Tool call returns error | Retry once. If still failing, tell the user: "Swiggy seems to be having issues. Try again in a minute, and make sure the Swiggy app is closed." |
| Search returns no results | Try broader terms. "paneer tikka" → "paneer" → "cottage cheese". |
| Checkout fails | Verify address is set (`get_addresses`). Verify cart is not empty (`get_cart`). Try again. |
| Session conflict | Ask: "Do you have the Swiggy app open? Please close it and I'll retry." |
| Product out of stock | Search for alternatives: different brand, different pack size. Tell the user. |
| Address not set | `get_addresses`, show options, ask user to pick one before proceeding. |
