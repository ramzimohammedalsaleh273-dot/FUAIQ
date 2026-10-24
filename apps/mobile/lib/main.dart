import 'dart:io';
import 'dart:typed_data';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:fuaiq_mobile/image_processor.dart';
import 'package:image_picker/image_picker.dart';
import 'package:path_provider/path_provider.dart';
import 'package:share_plus/share_plus.dart';

void main() => runApp(const FuaiqApp());

class FuaiqApp extends StatelessWidget {
  const FuaiqApp({super.key});
  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'فائق | FUAIQ',
    debugShowCheckedModeBanner: false,
    theme: ThemeData(useMaterial3: true,
      colorScheme: ColorScheme.fromSeed(seedColor: const Color(0xFF24617B))),
    home: const Directionality(textDirection: TextDirection.rtl, child: HomeScreen()),
  );
}

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});
  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  final _picker = ImagePicker();
  Uint8List? _originalBytes;
  Uint8List? _resultBytes;
  String? _savedPath;
  bool _busy = false;
  bool _showOriginal = false;
  double _sharpen = 0.35;
  double _contrast = 1.03;
  int _scale = 2;
  String? _error;

  Future<void> _chooseImage() async {
    try {
      // Do not request recompression; retain the selected source bytes where the picker permits.
      final file = await _picker.pickImage(source: ImageSource.gallery);
      if (file == null || !mounted) return;
      final bytes = await file.readAsBytes();
      setState(() { _originalBytes = bytes; _resultBytes = null; _savedPath = null; _error = null; });
    } catch (e) {
      if (mounted) setState(() => _error = 'تعذر فتح الصورة: $e');
    }
  }

  Future<void> _enhance() async {
    if (_originalBytes == null || _busy) return;
    setState(() { _busy = true; _error = null; });
    try {
      final bytes = await compute(processImageBytes, <String, Object>{
        'bytes': _originalBytes!, 'sharpen': _sharpen, 'contrast': _contrast, 'scale': _scale,
      });
      final dir = await getApplicationDocumentsDirectory();
      final out = File('${dir.path}/fuaiq_${DateTime.now().millisecondsSinceEpoch}.png');
      await out.writeAsBytes(bytes, flush: true);
      if (!mounted) return;
      setState(() { _resultBytes = bytes; _savedPath = out.path; _showOriginal = false; });
    } catch (e) {
      if (mounted) setState(() => _error = 'لم تنجح المعالجة: $e');
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  Future<void> _shareResult() async {
    final path = _savedPath;
    if (path == null || !File(path).existsSync()) {
      setState(() => _error = 'لا توجد نتيجة محفوظة لمشاركتها.');
      return;
    }
    try {
      await Share.shareXFiles([XFile(path)], text: 'تم تحسين الصورة باستخدام فائق FUAIQ');
    } catch (e) {
      if (mounted) setState(() => _error = 'تعذرت مشاركة الصورة: $e');
    }
  }

  @override
  Widget build(BuildContext context) => Scaffold(
    appBar: AppBar(title: const Row(children: [Icon(Icons.auto_awesome), SizedBox(width: 10), Text('فائق')])),
    body: SafeArea(child: ListView(padding: const EdgeInsets.all(16), children: [
      Container(padding: const EdgeInsets.all(20), decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(22),
        gradient: const LinearGradient(colors: [Color(0xFF101B27), Color(0xFF24516A)])),
        child: const Column(crossAxisAlignment: CrossAxisAlignment.start, children: [
          Text('استوديو الصور', style: TextStyle(color: Colors.white, fontSize: 24, fontWeight: FontWeight.bold)),
          SizedBox(height: 8),
          Text('معالجة محلية على الجهاز. لا تُرفع صورك إلى خادم.', style: TextStyle(color: Color(0xFFD6E7EF))),
        ])),
      const SizedBox(height: 16),
      OutlinedButton.icon(onPressed: _busy ? null : _chooseImage,
        icon: const Icon(Icons.add_photo_alternate_outlined), label: const Text('اختر صورة من الجهاز')),
      if (_originalBytes != null) ...[
        const SizedBox(height: 12),
        SegmentedButton<bool>(segments: const [
          ButtonSegment(value: false, label: Text('النتيجة')),
          ButtonSegment(value: true, label: Text('الأصل')),
        ], selected: {_showOriginal}, onSelectionChanged: _busy ? null : (v) => setState(() => _showOriginal = v.first)),
        const SizedBox(height: 10),
        ClipRRect(borderRadius: BorderRadius.circular(16), child: Image.memory(
          (_showOriginal || _resultBytes == null) ? _originalBytes! : _resultBytes!,
          fit: BoxFit.contain, errorBuilder: (_, __, ___) => const Text('تعذر عرض الصورة'))),
        const SizedBox(height: 12),
        Text('حدة التفاصيل: ${_sharpen.toStringAsFixed(2)}'),
        Slider(value: _sharpen, min: 0, max: 1, divisions: 20,
          label: _sharpen.toStringAsFixed(2), onChanged: _busy ? null : (v) => setState(() => _sharpen = v)),
        Text('التباين: ${_contrast.toStringAsFixed(2)}'),
        Slider(value: _contrast, min: 0.8, max: 1.3, divisions: 20,
          label: _contrast.toStringAsFixed(2), onChanged: _busy ? null : (v) => setState(() => _contrast = v)),
        const Text('التكبير'),
        SegmentedButton<int>(segments: const [
          ButtonSegment(value: 1, label: Text('1×')),
          ButtonSegment(value: 2, label: Text('2×')),
          ButtonSegment(value: 4, label: Text('4×')),
        ], selected: {_scale}, onSelectionChanged: _busy ? null : (v) => setState(() => _scale = v.first)),
        const SizedBox(height: 12),
        FilledButton.icon(onPressed: _busy ? null : _enhance,
          icon: _busy ? const SizedBox(width: 18, height: 18, child: CircularProgressIndicator(strokeWidth: 2)) : const Icon(Icons.auto_fix_high),
          label: Text(_busy ? 'جارٍ التحسين…' : 'حسّن الصورة واحفظ النتيجة')),
        if (_savedPath != null) ...[
          const SizedBox(height: 8),
          OutlinedButton.icon(onPressed: _busy ? null : _shareResult,
            icon: const Icon(Icons.share), label: const Text('مشاركة النتيجة أو حفظها في تطبيق آخر')),
          SelectableText('مسار الملف المحفوظ داخل التطبيق:\n$_savedPath'),
        ],
      ],
      if (_error != null) Padding(padding: const EdgeInsets.only(top: 12),
        child: Text(_error!, style: TextStyle(color: Theme.of(context).colorScheme.error))),
      const SizedBox(height: 12),
      const Text('تنبيه: هذه معالجة تقليدية محلية وليست نموذج ذكاء اصطناعي متخصصًا لإزالة الغباش. التكبير لا يستعيد بالضرورة تفاصيل مفقودة.',
        style: TextStyle(fontSize: 12, height: 1.5)),
    ])),
  );
}
