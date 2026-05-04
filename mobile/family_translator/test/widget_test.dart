import 'package:flutter_test/flutter_test.dart';
import 'package:provider/provider.dart';
import 'package:family_translator/main.dart';
import 'package:family_translator/providers/locale_provider.dart';

void main() {
  testWidgets('App loads smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(
      ChangeNotifierProvider(
        create: (_) => LocaleProvider(),
        child: const FamilyTranslatorApp(),
      ),
    );

    expect(find.text('🔮 Family Translator'), findsOneWidget);
  });
}
