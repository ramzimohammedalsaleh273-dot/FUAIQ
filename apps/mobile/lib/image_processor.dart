import 'dart:typed_data';
import 'package:image/image.dart' as img;

Uint8List processImageBytes(Map<String, Object> args) {
  final sourceBytes = args['bytes'] as Uint8List;
  final sharpen = args['sharpen'] as double;
  final contrast = args['contrast'] as double;
  final scale = args['scale'] as int;
  if (sharpen < 0 || sharpen > 1) throw ArgumentError.value(sharpen, 'sharpen');
  if (contrast < 0.8 || contrast > 1.3) throw ArgumentError.value(contrast, 'contrast');
  if (![1, 2, 4].contains(scale)) throw ArgumentError.value(scale, 'scale');
  final decoded = img.decodeImage(sourceBytes);
  if (decoded == null) throw const FormatException('صيغة الصورة غير مدعومة أو الملف تالف.');
  if (decoded.width * decoded.height > 40000000) {
    throw const FormatException('الصورة كبيرة جدًا؛ الحد 40 مليون بكسل.');
  }
  var work = img.bakeOrientation(decoded);
  work = img.adjustColor(work, contrast: contrast);
  if (sharpen > 0) {
    final amount = sharpen * 0.12;
    work = img.convolution(work, filter: [
      0, -amount, 0, -amount, 1 + 4 * amount, -amount, 0, -amount, 0
    ]);
  }
  if (scale > 1) {
    final width = work.width * scale, height = work.height * scale;
    if (width * height > 40000000) {
      throw const FormatException('الناتج يتجاوز حد 40 مليون بكسل. اختر تكبيرًا أقل.');
    }
    work = img.copyResize(work, width: width, height: height, interpolation: img.Interpolation.cubic);
  }
  return Uint8List.fromList(img.encodePng(work));
}
