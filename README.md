# FUAIQ — فائق

مشروع مفتوح المصدر لتحسين الصور، مع أولوية للحفاظ على الصورة الأصلية والشفافية بشأن حدود المعالجة. يتضمن الإصدار الحالي محرك Python محليًا وواجهة هاتف Flutter أولية تنفذ اختيار الصورة والمعالجة التقليدية على الجهاز.

## الوظائف الموجودة
- محرك Python: تصحيح اتجاه EXIF، تقليل تشويش اختياري، ضبط التباين، شحذ، وتكبير Lanczos ‏1×/2×/4×.
- عدم الكتابة فوق الصورة الأصلية، والتحقق من الصيغ والأبعاد وملف الناتج.
- ملف JSON جانبي يوثق إعدادات المعالجة والتحذيرات.
- واجهة أوامر واختبارات آلية وواجهة API محلية اختيارية.
- واجهة هاتف عربية: اختيار صورة من المعرض، معاينة الأصل/النتيجة، ضبط الشحذ والتكبير، وحفظ PNG في مجلد مستندات التطبيق.
- سير عمل GitHub Actions لاختبارات Python وFlutter ومحاولة بناء APK ونشره كأثر CI.

## تشغيل محرك Python على Windows (PowerShell)
```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
python -m unittest discover -s tests -v
```

## تحسين صورة عبر سطر الأوامر
```powershell
fuaiq enhance "C:\Users\Public\Pictures\input.jpg" --output "C:\Users\Public\Pictures\input_fuaiq.png" --scale 2
```
أو دون تثبيت أمر الدخول: `python -m fuaiq.cli enhance "input.jpg" --output "output.png" --scale 2`.

## تشغيل API محلية (اختياري)
```powershell
pip install -e ".[api]"
uvicorn fuaiq.api:app --host 127.0.0.1 --port 8000
```
ثم افتح `http://127.0.0.1:8000/docs`. لا تعرض الخدمة للإنترنت العام دون مصادقة وحدود استخدام وسياسة احتفاظ وحذف آمنة.

## تشغيل تطبيق الهاتف
تحتاج إلى تثبيت Flutter SDK وAndroid SDK. من مجلد `apps/mobile`:
```powershell
flutter create --platforms=android --project-name fuaiq_mobile --no-pub .
flutter pub get
flutter analyze
flutter test
flutter run
flutter build apk --release
```
يوجد أيضًا سير عمل GitHub Actions لبناء APK ورفعه كـ Artifact عند نجاح خطوات CI. لم يُتحقق من بناء APK محليًا في بيئة التطوير الحالية.

## حدود الجودة والنواقص
المعالجة الحالية تقليدية وليست نموذج ذكاء اصطناعي متخصصًا لإزالة الغباش أو اهتزاز اليد أو ترميم الوجوه أو رفع الدقة العصبي. التكبير يزيد عدد البكسلات ولا يضمن استعادة تفاصيل لم تُلتقط أصلًا. معالجة الهاتف مستقلة بلغة Dart ولا تتصل بمحرك Python، والنتيجة تحفظ داخل مستندات التطبيق؛ مشاركة الملف أو حفظه مباشرة في معرض الصور لم يضاف بعد. لا توجد حاليًا معالجة سحابية أو حسابات مستخدمين.

راجع `docs/ROADMAP.md`, `docs/QUALITY_PLAN.md`, و`docs/PRIVACY.md`.
