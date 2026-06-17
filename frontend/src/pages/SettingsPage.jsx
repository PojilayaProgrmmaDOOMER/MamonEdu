import { useEffect, useState } from "react";
import { getMyProfile, updateMyProfile, uploadMyAvatar } from "../api/userApi";

function SettingsPage() {
  const [profile, setProfile] = useState(null);
  const [form, setForm] = useState({
    username: "",
    bio: "",
    avatar_url: "",
  });
  const [saving, setSaving] = useState(false);
  const [avatarFile, setAvatarFile] = useState(null);

  async function loadProfile() {
    const data = await getMyProfile();

    setProfile(data);
    setForm({
      username: data.username || "",
      bio: data.bio || "",
      avatar_url: data.avatar_url || "",
    });
  }

  useEffect(() => {
    loadProfile();
  }, []);

  async function handleSubmit(event) {
    event.preventDefault();

    setSaving(true);

    try {
      let updatedForm = { ...form };

      if (avatarFile) {
        const uploaded = await uploadMyAvatar(avatarFile);
        updatedForm.avatar_url = uploaded.avatar_url;
      }

      const updated = await updateMyProfile(updatedForm);
      setProfile(updated);
      alert("Профиль сохранён");
    } finally {
      setSaving(false);
    }
  }

  if (!profile) {
    return <p>Загрузка профиля...</p>;
  }

  return (
    <div className="settings-page">
      <section className="settings-card">
        <div className="settings-profile-head">
          <div className="settings-avatar">
            {form.avatar_url ? (
              <img
                src={
                  form.avatar_url?.startsWith("/static")
                    ? `http://127.0.0.1:8000${form.avatar_url}`
                    : form.avatar_url
                }
                alt=""
              />
            ) : (
              <span>{form.username?.[0]?.toUpperCase() || "U"}</span>
            )}
          </div>

          <div>
            <h2>{profile.username}</h2>
            <p>{profile.role}</p>
          </div>
        </div>

        <form className="settings-form" onSubmit={handleSubmit}>
          <label>
            Имя пользователя
            <input
              value={form.username}
              onChange={(e) =>
                setForm({
                  ...form,
                  username: e.target.value,
                })
              }
            />
          </label>

          <label>
            Описание профиля
            <textarea
              rows="5"
              value={form.bio}
              onChange={(e) =>
                setForm({
                  ...form,
                  bio: e.target.value,
                })
              }
              placeholder="Например: преподаватель курса по компьютерному зрению..."
            />
          </label>

          <label>
            Загрузить аватар
            <input
              type="file"
              accept="image/*"
              onChange={(e) => setAvatarFile(e.target.files[0])}
            />
          </label>

          <label>
            Ссылка на аватар
            <input
              value={form.avatar_url}
              onChange={(e) =>
                setForm({
                  ...form,
                  avatar_url: e.target.value,
                })
              }
              placeholder="https://..."
            />
          </label>

          <button type="submit" disabled={saving}>
            {saving ? "Сохранение..." : "Сохранить профиль"}
          </button>
        </form>
      </section>
    </div>
  );
}

export default SettingsPage;