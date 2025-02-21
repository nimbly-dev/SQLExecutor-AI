import axios from 'axios';
import Cookies from 'js-cookie';
import { BASE_URL } from 'utils/apiConfig';
import { Ruleset, RulesetResponse, RulesetFilters, AddUpdateRulesetRequest } from 'types/ruleset/rulesetType';

const API_URL = `${BASE_URL}/v1/ruleset-manager`;

export const getRulesetByName = async (name: string): Promise<Ruleset> => {
  const token = Cookies.get('token');
  const tenant_id = Cookies.get('tenant_id');

  try {
    const params = new URLSearchParams({ name });
    const response = await axios.get(
      `${API_URL}/${tenant_id}/ruleset?${params}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      throw new Error('Ruleset not found');
    }
    throw new Error('Failed to fetch ruleset');
  }
};

export const getRulesetsPaginated = async ({
  name,
  filterName,
  isRulesetEnabled,
  hasInjectors,
  page = 1,
  pageSize = 10,
}: Partial<RulesetFilters>): Promise<RulesetResponse> => {
  const token = Cookies.get('token');
  const tenant_id = Cookies.get('tenant_id');
  
  const params = new URLSearchParams({
    summary_paginated: 'true',
    page: page.toString(),
    page_size: pageSize.toString(),
  });

  if (name?.trim()) params.append('name', name.trim());
  if (filterName?.trim()) params.append('filter_name', filterName.trim());
  if (isRulesetEnabled !== undefined) params.append('is_ruleset_enabled', isRulesetEnabled.toString());
  if (hasInjectors !== undefined) params.append('has_injectors', hasInjectors.toString());

  try {
    const response = await axios.get(
      `${API_URL}/${tenant_id}/ruleset?${params}`,
      { headers: { Authorization: `Bearer ${token}` } }
    );
    
    return response.data;
  } catch (error) {
    if (axios.isAxiosError(error) && error.response?.status === 404) {
      return {
        rulesets: [],
        total: 0,
        page: 1,
        page_size: pageSize
      };
    }
    throw error;
  }
};

export const deleteRuleset = async (rulesetName: string): Promise<void> => {
  const token = Cookies.get('token');
  const tenantId = Cookies.get('tenant_id');
  
  try {
    await axios.delete(`${API_URL}/${tenantId}/ruleset/${rulesetName}`, {
      headers: { Authorization: `Bearer ${token}` }
    });
  } catch (error) {
    console.error('Delete ruleset error:', error);
    throw error;
  }
};

export const addRuleset = async (rulesetData: AddUpdateRulesetRequest): Promise<Ruleset> => {
  const token = Cookies.get('token');
  const tenant_id = Cookies.get('tenant_id');
  
  try {
    const response = await axios.post(`${API_URL}/${tenant_id}/ruleset`, rulesetData, {
      headers: { Authorization: `Bearer ${token}` }
    });
    return response.data;
  } catch (error) {
    console.error('Add ruleset error:', error);
    throw error;
  }
}

export const updateRuleset = async (name: string, rulesetData: Partial<Ruleset>): Promise<Ruleset> => {
  const token = Cookies.get('token');
  const tenant_id = Cookies.get('tenant_id');

  try {
    const response = await axios.put(
      `${API_URL}/${tenant_id}/ruleset/${name}`,
      rulesetData,
      {
        headers: {
          Authorization: `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      }
    );
    return response.data.ruleset || response.data;
  } catch (error) {
    console.error('Update ruleset error:', error);
    throw error;
  }
};
