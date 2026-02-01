# Quick Start - Testing Infrastructure

Get started with the new testing infrastructure in 5 minutes!

## 🚀 Quick Start

### Step 1: Verify Setup

```bash
# Run verification script
python verify_testing.py
```

Expected output:
```
✅ All verification tests passed!
```

### Step 2: Run Unit Tests (Fast)

```bash
# Run all unit tests (~10 seconds)
python -m unittest discover -s tests/unit -v
```

### Step 3: Run API Tests (Mocked)

```bash
# Run API tests with mocks (~15 seconds)
python -m unittest discover -s tests/integration -p "test_api*.py" -v
```

### Step 4: (Optional) Setup ERPNext Testing

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your ERPNext credentials
ERPNEXT_URL=http://localhost:8080
ERPNEXT_API_KEY=your_api_key
ERPNEXT_API_SECRET=your_api_secret
```

### Step 5: (Optional) Run ERPNext Tests

```bash
# Run real ERPNext integration tests
python -m unittest discover -s tests/integration -p "test_erpnext*.py" -v
```

---

## 📋 What's New?

### 1. ERPNext Integration Tests (Real Connection)
- **`tests/integration/test_erpnext_real.py`** - Tests actual ERPNext API
- **`tests/integration/test_erpnext_workflows.py`** - Complete workflow tests
- Auto-skip if ERPNext not configured

### 2. ERPNext API Tests (Mocked)
- **`tests/integration/test_erpnext_api.py`** - All 7 endpoints tested
- Uses mocks - no ERPNext required
- Validates error handling

### 3. Test Fixtures
- **`tests/fixtures/erpnext_fixtures.py`** - Reusable test data
- Companies, suppliers, customers, items
- Complete PO and invoice data

### 4. Enhanced CI/CD
- **`.github/workflows/ci.yml`** - Updated pipeline
- Separate test execution (unit, API, ERPNext)
- ERPNext tests optional (won't block CI)

### 5. Documentation
- **`TESTING_GUIDE.md`** - Complete testing guide
- **`TESTING_IMPLEMENTATION_SUMMARY.md`** - Implementation overview
- **`verify_testing.py`** - Quick verification script

---

## 🧪 Test Commands Cheat Sheet

```bash
# Verify setup
python verify_testing.py

# Run all tests
python -m unittest discover -s tests -p "test_*.py" -v

# Run unit tests only (fast)
python -m unittest discover -s tests/unit -v

# Run API tests only (mocked)
python -m unittest discover -s tests/integration -p "test_api*.py" -v

# Run ERPNext tests only (real)
python -m unittest discover -s tests/integration -p "test_erpnext*.py" -v

# Run specific test file
python -m unittest tests.integration.test_erpnext_api -v

# Run specific test
python -m unittest tests.integration.test_erpnext_api.TestERPNextAPIEndpoints.test_get_company_success -v

# Run with coverage
coverage run -m unittest discover -s tests -p "test_*.py"
coverage report
```

---

## 📊 Test Overview

| Test Type | Files | Tests | Requires ERPNext | Time |
|-----------|-------|-------|------------------|------|
| Unit | 3 | 33 | No | ~10s |
| API (Mocked) | 4 | 42 | No | ~15s |
| ERPNext (Real) | 2 | 21 | Yes | ~30s |
| **Total** | **9** | **96** | - | **~55s** |

---

## ✅ Checklist

- [ ] Run `python verify_testing.py` - all pass?
- [ ] Run unit tests - all pass?
- [ ] Run API tests - all pass?
- [ ] (Optional) Configure `.env` for ERPNext
- [ ] (Optional) Run ERPNext tests
- [ ] Read `TESTING_GUIDE.md` for details
- [ ] CI pipeline passing on GitHub?

---

## 🔍 Troubleshooting

### Tests fail with import errors?
```bash
# Make sure you're in project root
cd InvoicePOParser
python -m unittest discover -s tests -v
```

### ERPNext tests always skip?
```bash
# Check .env file exists
cat .env

# Verify credentials
python -c "from app.services.erpnext_service import test_connection; print(test_connection())"
```

### Need help?
- See **`TESTING_GUIDE.md`** (Troubleshooting section)
- Check test file docstrings
- Review CI logs on GitHub

---

## 📚 Documentation

- **Quick Start**: This file
- **Complete Guide**: `TESTING_GUIDE.md`
- **Implementation Summary**: `TESTING_IMPLEMENTATION_SUMMARY.md`
- **Main README**: `README.md`

---

## 🎉 You're Ready!

```bash
# Start testing!
python verify_testing.py
python -m unittest discover -s tests/unit -v
```

**Happy Testing! 🚀**
