class RuleConvertor:
    def convert_str_to_rule(string):
        rules = string.split(" and ")
        result_rules = []
        
        for rule in rules:
            result_rules.append(
                rule.split(" or ")
            )
            
        return result_rules
    
    def get_rule_info(string):
        opened_bracket_index = string.find("(")
        closed_bracket_index = string.find(")")
        
        rule_name = string[:opened_bracket_index]
        tag = string[opened_bracket_index + 1:closed_bracket_index]
        
        return rule_name, tag