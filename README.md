# Event_match

প্রতি ১৫ মিনিট পর পর GitHub Actions স্বয়ংক্রিয়ভাবে স্পোর্টস ডেটা আপডেট করে `matches.json` এ সংরক্ষণ করে।

## ফাইলসমূহ
- `updater.py` — সোর্স থেকে ডেটা এনে `matches.json` তৈরি করে
- `.github/workflows/update.yml` — স্বয়ংক্রিয় আপডেট ওয়ার্কফ্লো
- `requirements.txt` — Python ডিপেনডেন্সি
- `matches.json` — আপডেট হওয়া ম্যাচ ডেটা

## লোকালি চালাতে
```bash
pip install -r requirements.txt
python updater.py
```
