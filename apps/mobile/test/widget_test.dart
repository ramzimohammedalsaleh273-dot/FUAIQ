import 'package:flutter_test/flutter_test.dart';
import 'package:fuaiq_mobile/main.dart';

void main() {
  testWidgets('shows Arabic FUAIQ home screen and image selection action', (tester) async {
    await tester.pumpWidget(const FuaiqApp());
    expect(find.text('فائق'), findsOneWidget);
    expect(find.text('استوديو الصور'), findsOneWidget);
    expect(find.text('اختر صورة من الجهاز'), findsOneWidget);
  });
}
