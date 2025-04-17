# Activity Adaptations

This directory contains adaptation templates and examples for various physical education activities. Each activity type has its own directory with specific adaptations based on different needs and abilities.

## Directory Structure

- `strength/` - Adaptations for strength-based exercises
- `flexibility/` - Adaptations for flexibility exercises
- `endurance/` - Adaptations for endurance activities
- `balance/` - Adaptations for balance exercises
- `coordination/` - Adaptations for coordination activities

## Adaptation File Structure

Each adaptation file follows this JSON structure:

```json
{
    "activity": "exercise_name",
    "needs": {
        "physical": ["list_of_physical_needs"],
        "cognitive": ["list_of_cognitive_needs"],
        "sensory": ["list_of_sensory_needs"]
    },
    "environment": {
        "space": "space_requirements",
        "equipment": "equipment_requirements",
        "surface": "surface_requirements"
    },
    "adaptation_level": "beginner|intermediate|advanced",
    "modifications": {
        "form": "modified_form_description",
        "repetitions": number,
        "sets": number,
        "rest_time": number,
        "progression": "progression_path"
    },
    "safety_considerations": [
        "list_of_safety_considerations"
    ],
    "equipment_adaptations": {
        "required": ["list_of_required_equipment"],
        "optional": ["list_of_optional_equipment"]
    }
}
```

## Usage

1. Select the appropriate activity type directory
2. Use the template.json file as a base for new adaptations
3. Modify the fields according to the specific needs of the student
4. Save the file with a descriptive name

## Best Practices

- Always consider safety first
- Start with the most basic adaptation and progress gradually
- Document any equipment needs clearly
- Include specific progression paths
- Consider both physical and cognitive adaptations 