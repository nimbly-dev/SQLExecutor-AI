import React, { useState } from 'react';
import { Tabs, Tab, Box, Button } from '@mui/material';
import styles from 'styles/common/forms/WizardTabForm.module.scss';

interface ValidationRule {
  path: string;
  required?: boolean;
  requiredFields?: string[];
  validateFn?: (value: any) => boolean;
}

interface TabDefinition {
  label: string;
  component: React.ReactNode;
  validationRules?: ValidationRule[];
}

interface WizardTabFormProps<T> {
  tabs: TabDefinition[];
  onSave?: () => void;
  onCancel?: () => void;
  formData: T;
  isSubmitting?: boolean;
}

export const WizardTabForm = <T extends Record<string, any>>({ 
  tabs, 
  onSave, 
  onCancel,
  formData,
  isSubmitting = false
}: WizardTabFormProps<T>) => {
  const [currentTab, setCurrentTab] = useState<number>(0);

  const getNestedValue = (obj: any, path: string): any => {
    return path.split('.').reduce((acc, part) => {
      if (acc === null || acc === undefined) return acc;
      return acc[part];
    }, obj);
  };

  const isFieldEmpty = (value: any): boolean => {
    if (value === undefined || value === null) return true;
    if (typeof value === 'string') return value.trim() === '';
    if (Array.isArray(value)) return value.length === 0;
    if (typeof value === 'object') return Object.keys(value).length === 0;
    return false;
  };

  const validateField = (rule: ValidationRule): boolean => {
    const value = getNestedValue(formData, rule.path);
    
    if (rule.required && isFieldEmpty(value)) {
      return false;
    }

    if (rule.requiredFields) {
      const nestedObject = value as Record<string, any>;
      return !rule.requiredFields.some(field => 
        isFieldEmpty(getNestedValue(nestedObject, field))
      );
    }

    if (rule.validateFn) {
      return rule.validateFn(value);
    }

    return true;
  };

  const isTabValid = (tabIndex: number): boolean => {
    const currentTabDef = tabs[tabIndex];
    if (!currentTabDef.validationRules || !formData) return true;

    return !currentTabDef.validationRules.some(rule => !validateField(rule));
  };

  const canProceedToNextTab = (): boolean => {
    return isTabValid(currentTab);
  };

  const handleTabChange = (event: React.SyntheticEvent, newValue: number) => {
    if (isTabValid(currentTab)) {
      setCurrentTab(newValue);
    }
  };

  const handleNext = () => {
    if (isTabValid(currentTab)) {
      if (currentTab < tabs.length - 1) {
        setCurrentTab((prev) => prev + 1);
      } else {
        onSave && onSave();
      }
    }
  };

  const handleBack = () => {
    if (currentTab > 0) {
      setCurrentTab((prev) => prev - 1);
    }
  };

  const isTabDisabled = (tabIndex: number): boolean => {
    let highestValidatedTab = 0;
    
    for (let i = 0; i <= Math.max(currentTab, tabIndex); i++) {
      if (isTabValid(i)) {
        highestValidatedTab = i;
      } else {
        break;
      }
    }

    return tabIndex > highestValidatedTab + 1;
  };

  return (
    <Box>
      {/* Navigation Tabs */}
      <Tabs 
        value={currentTab} 
        onChange={handleTabChange} 
        variant="scrollable"
        className={styles.tabsContainer}
      >
        {tabs.map((tab, index) => (
          <Tab 
            key={index} 
            label={tab.label}
            disabled={isTabDisabled(index)}
          />
        ))}
      </Tabs>

      {/* Current Tab Content */}
      <Box className={styles.tabContent}>
        {tabs[currentTab].component}
      </Box>

      {/* Action Buttons */}
      <Box className={styles.buttonsContainer}>
        <Box className={styles.leftButtons}>
          {currentTab > 0 && (
            <Button 
              variant="outlined" 
              onClick={handleBack}
              disabled={isSubmitting}
            >
              Back
            </Button>
          )}
        </Box>
        <Box className={styles.rightButtons}>
          {onCancel && (
            <Button 
              variant="outlined" 
              onClick={onCancel}
              disabled={isSubmitting}
            >
              Cancel
            </Button>
          )}
          <Button
            variant="contained"
            color="primary"
            onClick={handleNext}
            disabled={!canProceedToNextTab() || isSubmitting}
          >
            {currentTab < tabs.length - 1 ? 'Next' : (isSubmitting ? 'Saving...' : 'Save Changes')}
          </Button>
        </Box>
      </Box>
    </Box>
  );
};
