# 📁 TradeBerg Frontend Structure

## ✅ **Organized User Management System**

### **API Client Layer**
```
src/lib/apis/user-management.ts
```
- **Purpose**: Centralized API client for all user management operations
- **Functions**:
  - `getUserProfile()` - Get user profile with stats
  - `updateUserProfile()` - Update profile info
  - `getUserCredits()` - Get credit balance
  - `purchaseCredits()` - Create Stripe checkout
  - `useCredits()` - Deduct credits
  - `getCreditTransactions()` - Get transaction history
  - `getPayments()` - Get payment history
  - `getSubscription()` - Get subscription details

### **Pages Structure**

#### **1. Profile Page**
```
src/routes/(app)/profile/+page.svelte
```
**Features**:
- View/edit user profile (username, full name, bio)
- Display avatar and email
- Show subscription tier badge
- Display statistics (credits, payments, API calls, logins)
- Quick action buttons (Buy Credits, Transactions, Payments, Subscription)

**Sections**:
- Profile Card (left sidebar)
- Credits Card
- Profile Information (editable)
- Statistics Grid
- Quick Actions

#### **2. Credits Page**
```
src/routes/(app)/credits/+page.svelte
```
**Features**:
- Display current credit balance
- Show total purchased and used
- Credit packages with pricing
- Buy credits (Stripe integration)
- Recent transaction history
- Transaction icons and colors

**Packages**:
- Starter: 100 credits for $15 ($0.150/credit)
- Pro: 500 credits for $60 ($0.120/credit) - POPULAR
- Enterprise: 2000 credits for $2

00 ($0.100/credit)

#### **3. User Menu Component**
```
src/lib/components/layout/Sidebar/UserMenu.svelte
```
**Features**:
- Clickable profile section (goes to /profile)
- Shows avatar, name, email
- Displays current credits
- "Buy More" button
- Subscription badge
- Fallback to existing user store if API fails

---

## 🎯 **Navigation Flow**

```
User Menu (Sidebar)
  ↓
Click Profile Section → /profile
  ↓
Profile Page
  ├─ Edit Profile
  ├─ View Stats
  └─ Quick Actions
      ├─ Buy Credits → /credits
      ├─ Transactions → /transactions
      ├─ Payments → /payments
      └─ Subscription → /subscription
```

---

## 📊 **Data Flow**

```
Frontend (Svelte)
  ↓
API Client (user-management.ts)
  ↓
Backend API (/api/user-management/*)
  ↓
Supabase Database
  ↓
Stripe (for payments)
```

---

## 🔧 **Backend Endpoints Used**

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/user-management/profile` | GET | Get user profile + stats |
| `/api/user-management/profile` | PUT | Update profile |
| `/api/user-management/credits` | GET | Get credit balance |
| `/api/user-management/credits/purchase` | POST | Create Stripe checkout |
| `/api/user-management/credits/use` | POST | Deduct credits |
| `/api/user-management/credits/transactions` | GET | Get transaction history |
| `/api/user-management/payments` | GET | Get payment history |
| `/api/user-management/subscription` | GET | Get subscription |

---

## 🎨 **Component Organization**

### **Reusable Components**
- User profile card
- Credit balance display
- Transaction list item
- Payment card
- Statistics grid

### **Pages to Create Next**
1. ✅ `/profile` - User profile page
2. ✅ `/credits` - Buy credits page
3. ⏳ `/transactions` - Full transaction history
4. ⏳ `/payments` - Payment history
5. ⏳ `/subscription` - Subscription management
6. ⏳ `/credits/success` - Payment success page

---

## 🚀 **How to Use**

### **1. View Profile**
```typescript
// User clicks profile section in menu
goto('/profile');
```

### **2. Buy Credits**
```typescript
// From profile or credits page
const pkg = { credits: 100, price: 15.00 };
await purchaseCredits(token, {
  amount: pkg.price,
  credits: pkg.credits,
  success_url: `${baseUrl}/credits/success`,
  cancel_url: `${baseUrl}/credits`
});
// Redirects to Stripe checkout
```

### **3. Use Credits**
```typescript
await useCredits(token, {
  credits: 10,
  description: 'API call to analyze chart',
  endpoint: '/api/tradeberg/analyze'
});
```

---

## 📝 **TypeScript Types**

All types are defined in `user-management.ts`:
- `UserProfile` - User profile data
- `UserStats` - User statistics
- `CreditTransaction` - Transaction record
- `Payment` - Payment record

---

## 🎯 **Next Steps**

1. ✅ Create API client
2. ✅ Create profile page
3. ✅ Create credits page
4. ✅ Update user menu
5. ⏳ Create transactions page
6. ⏳ Create payments page
7. ⏳ Create subscription page
8. ⏳ Add payment success/cancel pages
9. ⏳ Add loading states
10. ⏳ Add error handling

---

## 🔐 **Authentication**

All API calls require a JWT token:
```typescript
const token = localStorage.getItem('token');
const headers = {
  'Authorization': `Bearer ${token}`
};
```

---

## 💡 **Best Practices**

1. **Always check for token** before API calls
2. **Handle errors gracefully** with try/catch
3. **Show loading states** during API calls
4. **Redirect to login** if unauthorized (401)
5. **Use TypeScript types** for type safety
6. **Keep API client separate** from components
7. **Reuse components** where possible
8. **Follow naming conventions**:
   - Pages: `+page.svelte`
   - Components: `ComponentName.svelte`
   - APIs: `api-name.ts`

---

## 📦 **File Naming Convention**

```
✅ GOOD:
- user-management.ts (API client)
- +page.svelte (route page)
- UserProfile.svelte (component)

❌ BAD:
- userManagement.ts
- page.svelte
- userprofile.svelte
```

---

## 🎨 **Styling**

All pages use:
- Tailwind CSS classes
- Dark mode support (`dark:` prefix)
- Responsive design (`md:`, `lg:` breakpoints)
- Consistent spacing and colors
- Blue primary color (#2563eb)

---

## ✅ **Status**

- ✅ Backend API complete
- ✅ Database schema created
- ✅ API client created
- ✅ Profile page created
- ✅ Credits page created
- ✅ User menu updated
- ⏳ Additional pages pending
- ⏳ Testing required

---

**Last Updated**: November 12, 2025
**Version**: 1.0.0
**Status**: Ready for Testing
