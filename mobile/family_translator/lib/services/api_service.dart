import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/chart_model.dart';

/// API configuration
class ApiConfig {
  /// Change this to your backend URL
  /// For iOS simulator: http://127.0.0.1:8000
  /// For Android emulator: http://10.0.2.2:8000
  /// For physical device: your computer's local IP
  static const String baseUrl = 'http://127.0.0.1:8000';

  /// Dev premium bypass token
  static const String devPremiumToken = 'Bearer dev-premium';
}

class ApiService {
  static final ApiService _instance = ApiService._internal();
  factory ApiService() => _instance;
  ApiService._internal();

  final _client = http.Client();
  bool _isPremium = false;
  String _lang = 'zh-TW';

  bool get isPremium => _isPremium;
  set isPremium(bool value) => _isPremium = value;

  String get lang => _lang;
  set lang(String value) => _lang = value;

  Map<String, String> get _headers => {
    'Content-Type': 'application/json',
    if (_isPremium) 'Authorization': ApiConfig.devPremiumToken,
  };

  /// Free tier: Get basic chart
  Future<BasicChart> getBasicChart({
    required String name,
    required String gender,
    required String date,
    required String time,
    String location = 'taipei',
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/api/free/chart'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'name': name,
        'gender': gender,
        'date': date,
        'time': time,
        'location': location,
        'lang': _lang,
      }),
    );

    if (response.statusCode == 200) {
      return BasicChart.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load chart: ${response.body}');
    }
  }

  /// Free tier: Get basic compatibility
  Future<BasicCompatibility> getBasicCompatibility({
    required Map<String, dynamic> person1,
    required Map<String, dynamic> person2,
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/api/free/compatibility'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'person1': {...person1, 'lang': _lang},
        'person2': {...person2, 'lang': _lang},
        'lang': _lang,
      }),
    );

    if (response.statusCode == 200) {
      return BasicCompatibility.fromJson(jsonDecode(response.body));
    } else {
      throw Exception('Failed to load compatibility: ${response.body}');
    }
  }

  /// Premium tier: Get full personal report
  Future<FullReport> getFullReport({
    required String name,
    required String gender,
    required String date,
    required String time,
    String location = 'taipei',
    String tier = 'standard',
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/api/premium/full-report'),
      headers: _headers,
      body: jsonEncode({
        'name': name,
        'gender': gender,
        'date': date,
        'time': time,
        'location': location,
        'lang': _lang,
        'tier': tier,
      }),
    );

    if (response.statusCode == 200) {
      return FullReport.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 403) {
      throw Exception('PREMIUM_REQUIRED');
    } else {
      throw Exception('Failed to load full report: ${response.body}');
    }
  }

  /// Premium tier: Ask a question based on chart
  Future<AskResponse> askQuestion({
    required Map<String, dynamic> chart,
    required String question,
    String tier = 'standard',
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/api/premium/ask'),
      headers: _headers,
      body: jsonEncode({
        'chart': chart,
        'question': question,
        'lang': _lang,
        'tier': tier,
      }),
    );

    if (response.statusCode == 200) {
      return AskResponse.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 403) {
      throw Exception('PREMIUM_REQUIRED');
    } else {
      throw Exception('Failed to get answer: ${response.body}');
    }
  }

  /// Premium tier: Get family constellation report
  Future<FamilyReport> getFamilyReport({
    required List<Map<String, dynamic>> members,
    String tier = 'standard',
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/api/premium/family'),
      headers: _headers,
      body: jsonEncode({
        'members': members,
        'lang': _lang,
        'tier': tier,
      }),
    );

    if (response.statusCode == 200) {
      return FamilyReport.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 403) {
      throw Exception('PREMIUM_REQUIRED');
    } else {
      throw Exception('Failed to load family report: ${response.body}');
    }
  }

  /// Premium tier: Get annual destiny report
  Future<AnnualReport> getAnnualReport({
    required String name,
    required String gender,
    required String date,
    required String time,
    String location = 'taipei',
    int year = 2026,
    String tier = 'standard',
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/api/premium/annual'),
      headers: _headers,
      body: jsonEncode({
        'name': name,
        'gender': gender,
        'date': date,
        'time': time,
        'location': location,
        'year': year,
        'lang': _lang,
        'tier': tier,
      }),
    );

    if (response.statusCode == 200) {
      return AnnualReport.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 403) {
      throw Exception('PREMIUM_REQUIRED');
    } else {
      throw Exception('Failed to load annual report: ${response.body}');
    }
  }

  /// Premium tier: Get deep compatibility
  Future<DeepCompatibility> getDeepCompatibility({
    required Map<String, dynamic> person1,
    required Map<String, dynamic> person2,
    String tier = 'standard',
  }) async {
    final response = await _client.post(
      Uri.parse('${ApiConfig.baseUrl}/api/premium/compatibility-deep'),
      headers: _headers,
      body: jsonEncode({
        'person1': {...person1, 'lang': _lang},
        'person2': {...person2, 'lang': _lang},
        'lang': _lang,
        'tier': tier,
      }),
    );

    if (response.statusCode == 200) {
      return DeepCompatibility.fromJson(jsonDecode(response.body));
    } else if (response.statusCode == 403) {
      throw Exception('PREMIUM_REQUIRED');
    } else {
      throw Exception('Failed to load deep compatibility: ${response.body}');
    }
  }
}
