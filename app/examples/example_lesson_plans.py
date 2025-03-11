from datetime import date
from app.models.lesson_plan import (
    LessonPlan, Subject, GradeLevel, Standard, SmartGoal,
    Objective, Activity, Assessment, DifferentiationPlan
)

def get_pe_lesson_plan() -> LessonPlan:
    """Example PE lesson plan for basketball fundamentals."""
    return LessonPlan(
        teacher_name="Coach Smith",
        subject=Subject.PHYSICAL_EDUCATION,
        grade_level=GradeLevel.GRADE_9,
        unit_title="Basketball Fundamentals",
        lesson_title="Advanced Dribbling and Ball Control",
        week_of=date(2024, 3, 11),
        date=date(2024, 3, 13),
        period="3",
        duration=45,
        
        standards=[
            Standard(
                code="2.5.12.A.1",
                description="Explain and demonstrate ways to apply movement skills from one game, sport, dance, or recreational activity to another.",
                type="NJSLS-HPE"
            ),
            Standard(
                code="2.5.12.A.2",
                description="Analyze application of force and motion to sports skills.",
                type="NJSLS-HPE"
            )
        ],
        
        objectives=[
            Objective(
                smart_goal=SmartGoal(
                    specific="Master crossover dribble and behind-the-back dribbling techniques",
                    measurable="Complete advanced dribbling sequence with 85% accuracy",
                    achievable="Build upon basic dribbling skills from previous lessons",
                    relevant="Essential for advanced basketball gameplay",
                    time_bound="Master techniques by end of class period"
                ),
                description="Students will demonstrate advanced dribbling techniques including crossover and behind-the-back dribbling",
                assessment_criteria="Successfully complete advanced dribbling sequence with proper form and control",
                language_objective="Demonstrate understanding of basketball terminology: crossover, pivot, control dribble"
            )
        ],
        
        essential_question="How do advanced dribbling techniques enhance a player's ability to maintain ball control and create scoring opportunities?",
        do_now="Partner passing drill: chest pass, bounce pass, overhead pass (5 each)",
        
        materials_needed=[
            "Basketballs (1 per student)",
            "Cones for dribbling course",
            "Whistle",
            "Score sheets",
            "Visual aids showing dribbling techniques",
            "iPad for video analysis"
        ],
        
        anticipatory_set="Quick demonstration of how professional players use advanced dribbling in game situations (2-minute video clip)",
        
        direct_instruction="""
1. Review proper basic dribbling form (2 minutes)
2. Demonstrate crossover dribble technique:
   - Ball position and hand placement
   - Weight transfer and body positioning
   - Common mistakes to avoid
3. Demonstrate behind-the-back dribble:
   - Starting position and execution
   - Timing and coordination
   - Safety considerations
""",
        
        guided_practice=[
            Activity(
                name="Progressive Dribbling Practice",
                description="""
1. Students practice crossover dribble stationary
2. Add movement with crossover (walking)
3. Increase speed (jogging)
4. Add defensive pressure (shadow defense)
""",
                duration=15,
                materials=["Basketballs"],
                grouping="Pairs",
                teaching_phase="Guided Practice",
                modifications={
                    "ell": "Visual demonstrations and peer modeling",
                    "iep": "Reduced speed, modified movements",
                    "gifted": "Add multiple defenders",
                    "504": "Additional space between players"
                }
            ),
            Activity(
                name="Behind-the-Back Circuit",
                description="Students rotate through 4 stations practicing behind-the-back dribble with varying challenges",
                duration=10,
                materials=["Basketballs", "Cones"],
                grouping="Small Groups",
                teaching_phase="Guided Practice",
                modifications={
                    "ell": "Station instructions with pictures",
                    "iep": "Modified success criteria",
                    "gifted": "Complex patterns and combinations",
                    "504": "Extended practice time"
                }
            )
        ],
        
        independent_practice=[
            Activity(
                name="Advanced Dribbling Challenge Course",
                description="""
Students complete a timed obstacle course incorporating:
1. Crossover dribbles around cones
2. Behind-the-back dribble through lanes
3. Combination moves in open space
4. Speed dribbling with control
""",
                duration=10,
                materials=["Basketballs", "Cones", "Stopwatch"],
                grouping="Individual",
                teaching_phase="Independent Practice"
            )
        ],
        
        closure="Class discussion on when to use each dribbling technique in game situations. Student demonstrations of most improved skills.",
        
        assessments=[
            Assessment(
                type="Performance",
                description="Advanced Dribbling Skills Assessment",
                criteria=[
                    "Proper hand positioning during crossover",
                    "Smooth transition in behind-the-back dribble",
                    "Maintained control throughout movements",
                    "Appropriate speed and power",
                    "Strategic use of techniques"
                ],
                tools=["Rubric", "Video Analysis"],
                modifications={
                    "ell": "Demonstration-based assessment",
                    "iep": "Modified success criteria",
                    "gifted": "Additional challenge elements",
                    "504": "Extended time if needed"
                }
            )
        ],
        
        differentiation=DifferentiationPlan(
            ell_strategies={
                "language_domains": "Speaking, Listening, Reading",
                "proficiency_level": "Intermediate",
                "strategies": "Visual aids, demonstrations, word wall",
                "accommodations": "Bilingual instructions, peer support"
            },
            iep_accommodations={
                "equipment": "Modified basketballs (size/weight)",
                "pacing": "Additional practice time",
                "instructions": "Break down complex moves",
                "environment": "Reduced distractions"
            },
            section_504_accommodations={
                "physical": "Modified movement patterns",
                "environmental": "Additional space",
                "temporal": "Extended practice time",
                "instructional": "One-on-one guidance"
            },
            gifted_talented_enrichment={
                "challenges": "Complex dribbling combinations",
                "leadership": "Peer coaching opportunities",
                "extension": "Create new dribbling patterns",
                "depth": "Analysis of pro player techniques"
            }
        ),
        
        homework="Practice crossover and behind-the-back dribbling 15 minutes daily. Record attempts and successes.",
        notes="Focus on proper hand positioning and body control. Watch for students rushing movements.",
        reflection="Students showed enthusiasm for advanced techniques. More practice needed on speed control.",
        next_steps="Introduce combining dribbling techniques with passing in next lesson."
    )

def get_health_lesson_plan() -> LessonPlan:
    """Example Health lesson plan for nutrition."""
    return LessonPlan(
        teacher_name="Ms. Johnson",
        subject=Subject.HEALTH,
        grade_level=GradeLevel.GRADE_10,
        unit_title="Nutrition and Wellness",
        lesson_title="Understanding Macro and Micronutrients",
        week_of=date(2024, 3, 11),
        date=date(2024, 3, 14),
        period="4",
        duration=45,
        
        standards=[
            Standard(
                code="2.1.12.B.1",
                description="Determine the relationship of nutrition and physical activity to weight loss, weight gain, and weight maintenance.",
                type="NJSLS-HPE"
            ),
            Standard(
                code="2.1.12.B.2",
                description="Compare and contrast the dietary trends and eating habits of adolescents and young adults in the United States and other countries.",
                type="NJSLS-HPE"
            )
        ],
        
        objectives=[
            Objective(
                smart_goal=SmartGoal(
                    specific="Identify and explain the role of macronutrients in the body",
                    measurable="Create accurate nutrient analysis of sample meals with 90% accuracy",
                    achievable="Use food labels and nutrition guides as references",
                    relevant="Essential for making healthy food choices",
                    time_bound="Complete analysis by end of class period"
                ),
                description="Students will analyze and categorize nutrients in common foods",
                assessment_criteria="Correctly identify macronutrients and their functions in sample meals",
                language_objective="Use proper terminology for nutrients and their functions"
            )
        ],
        
        essential_question="How do different nutrients contribute to overall health and wellness?",
        do_now="Quick write: List everything you ate yesterday and categorize items as proteins, carbs, or fats",
        
        materials_needed=[
            "Food labels",
            "Nutrition guides",
            "Worksheets",
            "Sample meal plans",
            "Digital presentation",
            "Interactive nutrition software"
        ],
        
        anticipatory_set="Display various food items and have students guess which macronutrients are dominant in each",
        
        direct_instruction="""
1. Define and explain macronutrients:
   - Proteins: structure, function, sources
   - Carbohydrates: types, energy role, sources
   - Fats: essential functions, healthy vs. unhealthy
2. Discuss micronutrients:
   - Vitamins: water vs. fat soluble
   - Minerals: major and trace
   - Daily requirements
""",
        
        guided_practice=[
            Activity(
                name="Nutrient Detective",
                description="Students work in pairs to analyze food labels and identify macro/micronutrients",
                duration=15,
                materials=["Food labels", "Worksheets"],
                grouping="Pairs",
                teaching_phase="Guided Practice",
                modifications={
                    "ell": "Bilingual food labels",
                    "iep": "Simplified analysis sheet",
                    "gifted": "Additional nutrient relationships",
                    "504": "Large print materials"
                }
            )
        ],
        
        independent_practice=[
            Activity(
                name="Meal Plan Analysis",
                description="Create and analyze a balanced meal plan for one day",
                duration=15,
                materials=["Meal planning sheets", "Nutrition guides"],
                grouping="Individual",
                teaching_phase="Independent Practice"
            )
        ],
        
        closure="Gallery walk of created meal plans with peer feedback on nutrient balance",
        
        assessments=[
            Assessment(
                type="Formative",
                description="Nutrient Analysis Quiz",
                criteria=[
                    "Correct identification of macronutrients",
                    "Understanding of nutrient functions",
                    "Ability to analyze food labels",
                    "Application to meal planning"
                ],
                modifications={
                    "ell": "Simplified language",
                    "iep": "Modified format",
                    "gifted": "Advanced analysis questions",
                    "504": "Extended time"
                }
            )
        ],
        
        differentiation=DifferentiationPlan(
            ell_strategies={
                "language_domains": "Reading, Writing, Speaking",
                "proficiency_level": "Intermediate",
                "strategies": "Visual aids, word banks, translations",
                "accommodations": "Bilingual resources"
            },
            iep_accommodations={
                "materials": "Modified worksheets",
                "pacing": "Extended work time",
                "presentation": "Multi-modal instruction",
                "assessment": "Simplified rubrics"
            },
            section_504_accommodations={
                "materials": "Large print resources",
                "environmental": "Preferential seating",
                "organizational": "Structured worksheets",
                "behavioral": "Movement breaks"
            },
            gifted_talented_enrichment={
                "content": "Research specific nutrients",
                "process": "Advanced analysis tasks",
                "product": "Create teaching materials",
                "environment": "Independent study options"
            }
        ),
        
        homework="Track personal food intake for one day using provided nutrient checklist",
        notes="Students showed particular interest in sports nutrition applications",
        reflection="Good engagement with food label analysis. Need more time for meal planning next time.",
        next_steps="Connect macronutrients to energy systems in next lesson"
    )

def get_drivers_ed_lesson_plan() -> LessonPlan:
    """Example Driver's Education lesson plan."""
    return LessonPlan(
        teacher_name="Mr. Rodriguez",
        subject=Subject.DRIVERS_ED,
        grade_level=GradeLevel.GRADE_10,
        unit_title="Traffic Laws and Road Safety",
        lesson_title="Understanding Right of Way Rules",
        week_of=date(2024, 3, 11),
        date=date(2024, 3, 15),
        period="5",
        duration=45,
        
        standards=[
            Standard(
                code="2.1.12.D.5",
                description="Summarize New Jersey Motor Vehicle laws and regulations and determine their impact on health and safety.",
                type="NJSLS-HPE"
            )
        ],
        
        objectives=[
            Objective(
                smart_goal=SmartGoal(
                    specific="Master right of way rules for different traffic scenarios",
                    measurable="Score 90% or higher on scenario-based assessment",
                    achievable="Use visual aids and practice scenarios",
                    relevant="Essential for safe driving",
                    time_bound="Demonstrate mastery by end of class"
                ),
                description="Students will demonstrate understanding of right of way rules in various traffic situations",
                assessment_criteria="Correctly identify right of way in 9 out of 10 scenarios",
                language_objective="Use proper traffic terminology and explain rules clearly"
            )
        ],
        
        essential_question="How do right of way rules contribute to traffic safety and prevent accidents?",
        do_now="Analyze an intersection scenario and determine who has right of way",
        
        materials_needed=[
            "Traffic scenario cards",
            "NJ Driver Manual",
            "Interactive whiteboard",
            "Video clips",
            "Practice worksheets",
            "Simulation software"
        ],
        
        anticipatory_set="Video showing common right of way violations and their consequences",
        
        direct_instruction="""
1. Define right of way concept
2. Cover specific situations:
   - Intersections (controlled vs. uncontrolled)
   - Emergency vehicles
   - Pedestrians and cyclists
   - Special situations
3. Review common mistakes and misconceptions
""",
        
        guided_practice=[
            Activity(
                name="Scenario Analysis",
                description="Students analyze traffic scenarios and discuss right of way decisions",
                duration=20,
                materials=["Scenario cards", "Traffic diagrams"],
                grouping="Small Groups",
                teaching_phase="Guided Practice",
                modifications={
                    "ell": "Visual scenario cards",
                    "iep": "Step-by-step analysis guide",
                    "gifted": "Complex multi-vehicle scenarios",
                    "504": "Simplified diagrams"
                }
            )
        ],
        
        independent_practice=[
            Activity(
                name="Virtual Traffic Navigator",
                description="Students complete interactive scenarios identifying right of way",
                duration=15,
                materials=["Computers", "Simulation software"],
                grouping="Individual",
                teaching_phase="Independent Practice"
            )
        ],
        
        closure="Students create their own right of way scenarios and challenge classmates to solve them",
        
        assessments=[
            Assessment(
                type="Formative",
                description="Right of Way Scenario Test",
                criteria=[
                    "Correct application of rules",
                    "Understanding of exceptions",
                    "Recognition of safety priorities",
                    "Clear explanation of decisions"
                ],
                modifications={
                    "ell": "Bilingual instructions",
                    "iep": "Reduced question complexity",
                    "gifted": "Advanced scenarios",
                    "504": "Oral responses allowed"
                }
            )
        ],
        
        differentiation=DifferentiationPlan(
            ell_strategies={
                "language_domains": "Reading, Speaking, Listening",
                "proficiency_level": "Intermediate",
                "strategies": "Visual aids, translated materials",
                "accommodations": "Bilingual glossary"
            },
            iep_accommodations={
                "instruction": "Break down complex scenarios",
                "materials": "Modified practice sheets",
                "assessment": "Simplified scenarios",
                "pacing": "Additional practice time"
            },
            section_504_accommodations={
                "materials": "High contrast visuals",
                "environmental": "Reduced distractions",
                "instructional": "Frequent checks",
                "behavioral": "Stress management strategies"
            },
            gifted_talented_enrichment={
                "content": "Research traffic laws",
                "process": "Create teaching scenarios",
                "product": "Develop safety presentations",
                "extension": "Analyze accident reports"
            }
        ),
        
        homework="Complete online practice scenarios and document challenging situations",
        notes="Students struggle most with uncontrolled intersection scenarios",
        reflection="Interactive scenarios were highly effective. Consider adding more complex situations next time.",
        next_steps="Cover emergency vehicle right of way rules in detail next lesson"
    ) 