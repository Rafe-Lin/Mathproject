# import_dependencies.py

from app import app, db, Skill, SkillDependency

# The dependency map we defined for trigonometry
# Format: (target_skill_name, prerequisite_skill_name)
DEPENDENCIES = [
    ('trig_ratios_general_angle', 'trig_ratios_right_triangle'),
    ('polar_coordinates', 'trig_ratios_general_angle'),
    ('radian_measure', 'polar_coordinates'),
    ('trig_properties_laws', 'radian_measure'),
    ('trig_graphs_periodicity', 'trig_properties_laws'),
    ('trig_sum_difference', 'trig_graphs_periodicity'),
    ('trig_sine_cosine_combination', 'trig_sum_difference'),
]

def import_dependencies():
    """
    Imports the defined skill dependencies into the database.
    """
    with app.app_context():
        print("Starting to import skill dependencies...")
        
        # Clear existing dependencies to avoid duplicates if run multiple times
        # This is a simple approach; for complex graphs, a more targeted update would be better.
        try:
            num_deleted = db.session.query(SkillDependency).delete()
            if num_deleted > 0:
                print(f"Cleared {num_deleted} existing dependencies.")
        except Exception as e:
            print(f"Error clearing old dependencies: {e}")
            db.session.rollback()
            return

        for target_name, prereq_name in DEPENDENCIES:
            # Find the skill objects from the database
            target_skill = Skill.query.filter_by(name=target_name).first()
            prereq_skill = Skill.query.filter_by(name=prereq_name).first()

            if not target_skill:
                print(f"!! WARNING: Target skill '{target_name}' not found in database. Skipping.")
                continue
            if not prereq_skill:
                print(f"!! WARNING: Prerequisite skill '{prereq_name}' not found in database. Skipping.")
                continue

            # Check if the dependency already exists
            existing_dependency = SkillDependency.query.filter_by(
                target_id=target_skill.id,
                prerequisite_id=prereq_skill.id
            ).first()

            if existing_dependency:
                print(f"Dependency '{prereq_name}' -> '{target_name}' already exists. Skipping.")
            else:
                # Create and add the new dependency
                new_dependency = SkillDependency(
                    target_id=target_skill.id,
                    prerequisite_id=prereq_skill.id
                )
                db.session.add(new_dependency)
                print(f"-> Adding dependency: '{prereq_name}' -> '{target_name}'")

        # Commit the changes to the database
        try:
            db.session.commit()
            print("...Finished importing dependencies.")
        except Exception as e:
            print(f"Error committing new dependencies: {e}")
            db.session.rollback()

if __name__ == '__main__':
    import_dependencies()
