/// Free tier: basic chart data
class BasicChart {
  final String name;
  final String gender;
  final Map<String, dynamic> bazi;
  final Map<String, dynamic> astrology;
  final Map<String, dynamic> ziwei;
  final Map<String, dynamic> humandesign;
  final String xingxiu;
  final int energyScore;
  final String summary;
  final Map<String, dynamic> interpretations;

  BasicChart({
    required this.name,
    required this.gender,
    required this.bazi,
    required this.astrology,
    required this.ziwei,
    required this.humandesign,
    required this.xingxiu,
    required this.energyScore,
    required this.summary,
    required this.interpretations,
  });

  factory BasicChart.fromJson(Map<String, dynamic> json) {
    return BasicChart(
      name: json['name'] ?? '',
      gender: json['gender'] ?? '',
      bazi: json['bazi'] ?? {},
      astrology: json['astrology'] ?? {},
      ziwei: json['ziwei'] ?? {},
      humandesign: json['humandesign'] ?? {},
      xingxiu: json['xingxiu'] ?? '',
      energyScore: json['energy_score'] ?? 0,
      summary: json['summary'] ?? '',
      interpretations: json['interpretations'] ?? {},
    );
  }
}

/// Free tier: basic compatibility
class BasicCompatibility {
  final double overallScore;
  final String stars;
  final String summary;
  final Map<String, dynamic> dimensions;
  final String person1Summary;
  final String person2Summary;

  BasicCompatibility({
    required this.overallScore,
    required this.stars,
    required this.summary,
    required this.dimensions,
    required this.person1Summary,
    required this.person2Summary,
  });

  factory BasicCompatibility.fromJson(Map<String, dynamic> json) {
    return BasicCompatibility(
      overallScore: (json['overall_score'] as num?)?.toDouble() ?? 0.0,
      stars: json['stars'] ?? '',
      summary: json['summary'] ?? '',
      dimensions: json['dimensions'] ?? {},
      person1Summary: json['person1_summary'] ?? '',
      person2Summary: json['person2_summary'] ?? '',
    );
  }
}

/// Premium tier: full personal report
class FullReport {
  final BasicChart basic;
  final String integratedProfile;
  final Map<String, dynamic> strengthsWeaknesses;
  final String lifeLessons;
  final List<dynamic> prescription;

  FullReport({
    required this.basic,
    required this.integratedProfile,
    required this.strengthsWeaknesses,
    required this.lifeLessons,
    required this.prescription,
  });

  factory FullReport.fromJson(Map<String, dynamic> json) {
    return FullReport(
      basic: BasicChart.fromJson(json['basic'] ?? {}),
      integratedProfile: json['integrated_profile'] ?? '',
      strengthsWeaknesses: json['strengths_weaknesses'] ?? {},
      lifeLessons: json['life_lessons'] ?? '',
      prescription: json['prescription'] ?? [],
    );
  }
}

/// Premium tier: deep compatibility
class DeepCompatibility {
  final BasicCompatibility basic;
  final String relationshipNarrative;
  final List<dynamic> conflictPoints;
  final Map<String, dynamic> communicationGuide;
  final List<dynamic> prescription;

  DeepCompatibility({
    required this.basic,
    required this.relationshipNarrative,
    required this.conflictPoints,
    required this.communicationGuide,
    required this.prescription,
  });

  factory DeepCompatibility.fromJson(Map<String, dynamic> json) {
    return DeepCompatibility(
      basic: BasicCompatibility.fromJson(json['basic'] ?? {}),
      relationshipNarrative: json['relationship_narrative'] ?? '',
      conflictPoints: json['conflict_points'] ?? [],
      communicationGuide: json['communication_guide'] ?? {},
      prescription: json['prescription'] ?? [],
    );
  }
}

/// Premium tier: Q&A response
class AskResponse {
  final String answer;
  final List<String> relevantSystems;
  final String confidence;
  final String disclaimer;

  AskResponse({
    required this.answer,
    required this.relevantSystems,
    required this.confidence,
    required this.disclaimer,
  });

  factory AskResponse.fromJson(Map<String, dynamic> json) {
    return AskResponse(
      answer: json['answer'] ?? '',
      relevantSystems: List<String>.from(json['relevant_systems'] ?? []),
      confidence: json['confidence'] ?? '中',
      disclaimer: json['disclaimer'] ?? '本回答僅供參考，請理性判斷並以自身實際情況為準。',
    );
  }
}


/// Premium tier: family constellation report
class FamilyReport {
  final String familyNarrative;
  final List<dynamic> memberReports;
  final List<dynamic> relationshipMatrix;
  final List<dynamic> familyPrescription;
  final Map<String, dynamic> communicationGuide;

  FamilyReport({
    required this.familyNarrative,
    required this.memberReports,
    required this.relationshipMatrix,
    required this.familyPrescription,
    required this.communicationGuide,
  });

  factory FamilyReport.fromJson(Map<String, dynamic> json) {
    return FamilyReport(
      familyNarrative: json['family_narrative'] ?? '',
      memberReports: json['member_reports'] ?? [],
      relationshipMatrix: json['relationship_matrix'] ?? [],
      familyPrescription: json['family_prescription'] ?? [],
      communicationGuide: json['communication_guide'] ?? {},
    );
  }
}

/// Premium tier: annual destiny report
class MonthInsight {
  final int month;
  final String theme;
  final String advice;
  final String energy;

  MonthInsight({
    required this.month,
    required this.theme,
    required this.advice,
    required this.energy,
  });

  factory MonthInsight.fromJson(Map<String, dynamic> json) {
    return MonthInsight(
      month: json['month'] ?? 0,
      theme: json['theme'] ?? '',
      advice: json['advice'] ?? '',
      energy: json['energy'] ?? 'medium',
    );
  }
}

class AnnualReport {
  final String yearTheme;
  final String yearlyOverview;
  final Map<String, dynamic> baziLuck;
  final List<dynamic> keyOpportunities;
  final List<dynamic> keyChallenges;
  final List<MonthInsight> monthlyInsights;
  final List<dynamic> annualPrescription;

  AnnualReport({
    required this.yearTheme,
    required this.yearlyOverview,
    required this.baziLuck,
    required this.keyOpportunities,
    required this.keyChallenges,
    required this.monthlyInsights,
    required this.annualPrescription,
  });

  factory AnnualReport.fromJson(Map<String, dynamic> json) {
    return AnnualReport(
      yearTheme: json['year_theme'] ?? '',
      yearlyOverview: json['yearly_overview'] ?? '',
      baziLuck: json['bazi_luck'] ?? {},
      keyOpportunities: json['key_opportunities'] ?? [],
      keyChallenges: json['key_challenges'] ?? [],
      monthlyInsights: (json['monthly_insights'] as List?)
              ?.map((m) => MonthInsight.fromJson(m))
              .toList() ??
          [],
      annualPrescription: json['annual_prescription'] ?? [],
    );
  }
}
