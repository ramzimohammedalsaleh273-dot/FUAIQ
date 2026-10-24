# FUAIQ — فائق

تطبيق عربي لتحسين الصور، يبدأ بمعالجة محلية للحفاظ على الخصوصية. يحتوي المستودع على محرك Python وواجهة هاتف Flutter، مع اختبارات وأتمتة بناء. هذا إصدار تأسيسي قابل للتشغيل وليس منتجًا نهائيًا بمستوى ترميم الذكاء الاصطناعي المتخصص.

## وظائف موجودة الآن
- تصحيح اتجاه EXIF وفحص الصيغ وأبعاد الصور قبل فكها.
- تقليل تشويش تقليدي اختياري في محرك Python، وضبط التباين والشحذ.
- تكبير Lanczos حتى 4× في محرك Python؛ وفي الهاتف تكبير استيفائي محلي حتى 4×.
- حفظ نسخة ناتجة منفصلة مع بيانات وصفية عن خيارات المعالجة والتحذيرات.
- واجهة أوامر، واختبارات Python، وواجهة API محلية اختيارية مع حد لحجم الرفع.
- تطبيق هاتف عربي: اختيار صورة من المعرض، معاينة الأصل/النتيجة، ضبط التباين والشحذ والتكبير، معالجة في isolate منفصل لتقليل تجميد الواجهة، حفظ PNG داخل مستندات التطبيق ومشاركة الناتج عبر قائمة مشاركة النظام.
- GitHub Actions لاختبارات Python وFlutter وبناء APK كأثر عند نجاح سير العمل.

## محرك Python على Windows PowerShell
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m unittest discover -s tests -v
```

تحسين صورة:
```powershell
fuaiq enhance "C:\Users\Public\Pictures\input.jpg" --output "C:\Users\Public\Pictures\input_fuaiq.png" --scale 2
```

## API محلية اختيارية
```powershell
pip install -e ".[api]"
uvicorn fuaiq.api:app --host 127.0.0.1 --port 8000
```
ثم افتح `http://127.0.0.1:8000/docs`. لا تعرض API على الإنترنت العام دون مصادقة وضوابط خصوصية وأمان مناسبة.

## تطبيق Android
تحتاج إلى Flutter SDK وAndroid SDK. من داخل `apps/mobile`:
```powershell
flutter create --platforms=android --project-name fuaiq_mobile --no-pub .
flutter pub get
flutter analyze
flutter test
flutter run
flutter build apk --release
```

تابع سير العمل الآلي وملف APK إن نجح البناء:
https://github.com/ramzimohammedalsaleh273-dot/FUAIQ/actions

## نواقص معروفة لا يجوز اعتبارها منجزة
- لا يوجد نموذج ذكاء اصطناعي متخصص مدمج لإزالة الغباش أو اهتزاز اليد أو ترميم الوجوه أو رفع الدقة العصبي.
- لم يُتحقق بعد من نجاح بناء APK أو تشغيله على هاتف فعلي.
- لا توجد معالجة سحابية، أو حسابات مستخدمين، أو حفظ مباشر إلى معرض الصور من داخل التطبيق؛ يمكن مشاركة الملف إلى تطبيق آخر من قائمة النظام.
- معالجة الهاتف مستقلة عن محرك Python؛ ليست هناك طبقة مشتركة بينهما حاليًا.

التكبير يزيد عدد البكسلات ولا يضمن استعادة التفاصيل غير الموجودة في المصدر. راجع `docs/QUALITY_PLAN.md`, `docs/PRIVACY.md`, و`docs/ROADMAP.md`.
