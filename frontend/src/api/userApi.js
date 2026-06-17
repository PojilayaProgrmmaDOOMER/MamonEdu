import { api } from "./client";

export const getMyProfile = async () => {
  const response = await api.get("/users/me/profile");
  return response.data;
};

export const getMyProgress = async () => {
  const response = await api.get("/users/me/progress");
  return response.data;
};

export const getMyRecommendations = async () => {
  const response = await api.get("/users/me/recommendations");
  return response.data;
};

export const updateMyProfile = async (data) => {
  const response = await api.put("/users/me/profile", data);
  return response.data;
};

export const uploadMyAvatar = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await api.post("/users/me/avatar", formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

  return response.data;
};