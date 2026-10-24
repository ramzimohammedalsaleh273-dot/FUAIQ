import 'dart:typed_data';
import 'package:flutter_test/flutter_test.dart';
import 'package:image/image.dart' as img;
import 'package:fuaiq_mobile/image_processor.dart';

void main() {
  test('processes a valid image and scales output dimensions', () {
    final source = img.Image(width: 8, height: 6);
    source.clear(color: img.ColorRgb8(100, 120, 140));
    final input = Uint8List.fromList(img.encodePng(source));
    final output = processImageBytes({
      'bytes': input, 'sharpen': 0.3, 'contrast': 1.05, 'scale': 2,
    });
    final decoded = img.decodeImage(output);
    expect(decoded, isNotNull);
    expect(decoded!.width, 16);
    expect(decoded.height, 12);
  });

  test('rejects corrupt input bytes', () {
    expect(() => processImageBytes({
      'bytes': Uint8List.fromList([1, 2, 3, 4]),
      'sharpen': 0.3, 'contrast': 1.0, 'scale': 1,
    }), throwsFormatException);
  });

  test('rejects unsupported scale', () {
    expect(() => processImageBytes({
      'bytes': Uint8List.fromList([1]),
      'sharpen': 0.3, 'contrast': 1.0, 'scale': 3,
    }), throwsArgumentError);
  });
}
