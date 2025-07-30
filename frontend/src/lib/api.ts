const API_BASE_URL = "https://api.ar.boetus.com";

export interface TotalSessionsResponse {
  total_sessions: number;
}

export interface ActiveUsersResponse {
  active_users: number;
}

export interface BotCompletionStats {
  completion_percentage: number;
  number_of_total_steps: number;
}

export interface BotCompletionResponse {
  bot_completion_stats: Record<string, BotCompletionStats>;
}

export interface HumanValue {
  value: string;
  count: number;
  percentage: number;
}

export interface TopHumanValuesResponse {
  top_human_values: HumanValue[];
  total_values_analyzed: number;
}

export interface ChatbotRecommendation {
  recommendation: string;
  count: number;
  percentage: number;
}

export interface TopChatbotRecommendationsResponse {
  top_chatbot_recommendations: ChatbotRecommendation[];
  total_recommendations_analyzed: number;
}

export interface LeadershipChallenge {
  category: string;
  challenge_name: string;
  count: number;
  summaries: string[];
}

export interface TopLeadershipChallengesResponse {
  top_leadership_challenges: LeadershipChallenge[];
  total_challenges_analyzed: number;
}

class ApiService {
  private async fetchData<T>(endpoint: string): Promise<T> {
    console.log(`API_BASE_URL: ${API_BASE_URL}, endpoint: ${endpoint}`);
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch ${endpoint}: ${response.statusText}`);
    }
    return response.json();
  }

  async getTotalSessions(): Promise<TotalSessionsResponse> {
    return this.fetchData<TotalSessionsResponse>('/api/v1/dashboard/stats/total-sessions');
  }

  async getActiveUsers(): Promise<ActiveUsersResponse> {
    return this.fetchData<ActiveUsersResponse>('/api/v1/dashboard/stats/active-users');
  }

  async getBotCompletion(): Promise<BotCompletionResponse> {
    return this.fetchData<BotCompletionResponse>('/api/v1/dashboard/stats/bot-completion');
  }

  async getTopHumanValues(limit: number = 10): Promise<TopHumanValuesResponse> {
    return this.fetchData<TopHumanValuesResponse>(`/api/v1/dashboard/stats/top-human-values?limit=${limit}`);
  }

  async getTopChatbotRecommendations(limit: number = 10): Promise<TopChatbotRecommendationsResponse> {
    return this.fetchData<TopChatbotRecommendationsResponse>(`/api/v1/dashboard/stats/top-chatbot-recommendations?limit=${limit}`);
  }

  async getTopLeadershipChallenges(botNames: string[], limit: number = 6, num_summaries: number = 4): Promise<TopLeadershipChallengesResponse> {
    const botNamesParam = botNames.map(name => `bot_names=${encodeURIComponent(name)}`).join('&');
    return this.fetchData<TopLeadershipChallengesResponse>(`/api/v1/dashboard/stats/top-leadership-challenges?${botNamesParam}&limit=${limit}&num_summaries=${num_summaries}`);
  }
}

export const apiService = new ApiService();
