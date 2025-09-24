# Setup MinIO Deployment on Kubernetes (Operator v7.1.1+)
## ⚠️ Requirements
    - Kubernetes v1.30.0+
    - kubectl installed and configured
    - Sudo/root access on cluster nodes
    - Pre-created directories on worker nodes for persistent storage

## step 1 - Install the MinIO Operator via Kustomization:
```
kubectl kustomize github.com/minio/operator\?ref=v7.1.1 | kubectl apply -f -
```

## step 2 - Make local storageclass:
```
kubectl apply -f minio-local-storageclass.yaml
```

## step 3 - Make Persistent Volumes:

do thiếu điều kiện nên phải tạo folder thủ công rồi tạo vùng chứa bên trong chứ không được dùng nguyên ổ cứng mới toanh.

-> trên các máy nodes tạo các thư mục để lưu.
slave01
```
# Tạo thư mục chính
sudo mkdir -p /mnt/minio-disks

# Tạo 2 thư mục con (để có tổng cộng 4 ổ đĩa cho cả cụm)
sudo mkdir -p /mnt/minio-disks/disk1
sudo mkdir -p /mnt/minio-disks/disk2

# Gán quyền sở hữu cho user UID 1000
sudo chown -R 1000:1000 /mnt/minio-disks
```

slave02
```
sudo mkdir -p /mnt/minio-disks
sudo mkdir -p /mnt/minio-disks/disk1
sudo mkdir -p /mnt/minio-disks/disk2
sudo chown -R 1000:1000 /mnt/minio-disks
```

sau đó về master chạy khởi tạo PV (persistent volume)
```
kubectl apply -f pv-slave01.yaml
kubectl apply -f pv-slave02.yaml
```

kiểm tra pv bằng cách:
```
kubectl get pv
```

## Step cuối -  Build the Tenant Configuration
```
kubectl apply -k /base
```


## Kiểm tra đúng không:

kiểm tra vem PV và PVC đã bound chưa
```
kubectl get pvc -n minio-tenant
```

kiểm tra svc
```
kubectl get svc -n minio-tenant
```

kiểm tra tenants
```
kubectl get tenants -n minio-tenant
```

##  Truy cập MinIO Console
Forward cổng Console (9443)
```
kubectl port-forward svc/myminio-console -n minio-tenant 9443:9443
```

## Truy cập S3 API
```
kubectl port-forward svc/minio -n minio-tenant 9000:443
```

## NodePort để expose port
```
kubectl apply -f 'base/node-port/minio-console-nodeport.yaml'
kubectl apply -f 'base/node-port/minio-nodeport.yaml'
```